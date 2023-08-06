import opreport.helpers as helpers
import opreport.opsramp.objects as objects
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import pandas as pd
import matplotlib.pyplot as plt
import  matplotlib.dates as mdates
import os
from matplotlib.ticker import MaxNLocator


def report(openv, tenants, daterange, outdir, logo):
    (start, end, bl_start, bl_end, utc_offset) = daterange
    for tenant in tenants:
        print("Tenant is " + tenant['uniqueId'] + " - " + tenant['name'])

        #
        # Get resources, users, and console sessions for tenant
        #

        resources = {}
        resources_arr = objects.get_objects(openv, 'resources', tenant=tenant['uniqueId'])
        for resource in resources_arr:
            resources[resource['id']] = resource

        users = {}
        partner_users = objects.get_objects(openv, 'users', openv.env['partner'])
        for user in partner_users:
            users[user['id']] = user

        tenant_users = objects.get_objects(openv, 'users', tenant=tenant['uniqueId'])
        for user in tenant_users:
            users[user['id']] = user

        queryString = f'startDate:{datetime.strftime(start,"%Y-%m-%dT%H:%M:%S 0000")}+endDate:{datetime.strftime(end,"%Y-%m-%dT%H:%M:%S 0000")}'
        consoles = objects.get_objects(openv, 'consoleRecordings', tenant=tenant['uniqueId'], queryString=queryString)

        for (idx,console) in enumerate(consoles):
            local_start_dt = datetime.astimezone(datetime.strptime(console['startTime'],'%Y-%m-%dT%H:%M:%S%z'))
            local_start_string = datetime.strftime(local_start_dt, '%Y-%m-%d %H:%M:%S %Z')
            duration = "-"
            try:
                local_end_dt = datetime.strptime(console['endTime'],'%Y-%m-%dT%H:%M:%S%z')
                duration = local_end_dt - local_start_dt
            except:
                duration = "-"

            consoles[idx]['local_start_string'] = local_start_string 
            consoles[idx]['duration'] = duration 

        #
        # INITIALIZE PDF DOC
        #

        pdf = helpers.PDF_STD_HEADER_FOOTER(tenant, "Remote Control Usage Report", start, end, None, None, logo, 'P', 'mm', 'Letter')
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        #
        # SESSION BAR CHART
        #

        df = pd.DataFrame(pd.json_normalize(consoles))
        if len(df) > 0:
            df['date'] =  pd.to_datetime(df['local_start_string']).dt.date
            daily_counts = df.groupby(['date'])['date'].count().sort_index()
            daily_counts = pd.merge(pd.DataFrame(index=pd.date_range(start,end)[:-1].date),daily_counts, how='outer', left_index=True, right_index=True).fillna(0)
            plt.figure(figsize=(8,3), dpi=600)
            plt.bar(x=daily_counts.index, height=daily_counts['date'].values)
            ax=plt.gca()
            fig = ax.get_figure()
            fig.subplots_adjust(bottom=0.28)

            plt.title(f'Remote Control Sessions', fontsize=9, fontweight='bold')
            plt.xticks(rotation = 45, fontsize=6)
            plt.yticks(fontsize=7)
            if len(daily_counts) < 45:
                plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.gcf().autofmt_xdate()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            if len(daily_counts['date'].values) > 0:
                ax.set(xlim=[daily_counts['date'].index[0], daily_counts['date'].index[-1]])
            ax.grid(axis='y')
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            imagefile = f'{tenant["uniqueId"]}_remote_control_sessions.png'
            plt.savefig(imagefile, bbox_inches='tight')
            plt.clf()
            plt.close(fig)

            pdf.image(imagefile, x=pdf.l_margin, w=pdf.epw)
            os.remove(imagefile)

            pdf.ln(20)

            #
            # SESSION TYPES TABLE
            #

            session_types = df.groupby(['consoleProtocol'])['consoleProtocol'].count().to_frame()
            session_types['pct'] = session_types['consoleProtocol']/session_types['consoleProtocol'].sum()*100


            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(w=pdf.epw, txt=f'Managed Device Remote Control Sessions', align='L', ln=1)
            pdf.ln(5)


            pdf.set_fill_color(224, 102, 54)
            pdf.set_text_color(255,255,255)
            pdf.set_font('Helvetica', 'B', 9)
            line_height = pdf.font_size * 4
            col_width = pdf.epw / 6 # distribute content evenly as baseline

            pdf.multi_cell(col_width*1.25, line_height, 'Session Type', border='LTB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*1, line_height, 'Count', border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*1, line_height, 'Percentage', border='TBR', ln=1, max_line_height=pdf.font_size, fill=True, align='C')

            pdf.set_text_color(0,0,0)
            pdf.set_font('Helvetica', '', 7)
            line_height = pdf.font_size * 2
            i=0
            for (idx,rec) in session_types.iterrows():
                if i == 0:
                    pdf.set_fill_color(252, 245, 233)
                else:
                    pdf.set_fill_color(249, 234, 213)


                pdf.multi_cell(col_width*1.25, line_height, idx, border='LTB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
                pdf.multi_cell(col_width*1, line_height, '{:d}'.format(round(rec['consoleProtocol'])), border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
                pdf.multi_cell(col_width*1, line_height, "{:.1f}%".format(rec['pct']), border='TBR', ln=1, max_line_height=pdf.font_size, fill=True, align='C')
                i+=1

            pdf.set_font('Helvetica', 'B', 7)
            pdf.multi_cell(col_width*1.25, line_height, 'Total', border='LTB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*1, line_height, '{:d}'.format(round(session_types['consoleProtocol'].sum())), border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*1, line_height, ' ', border='TBR', ln=1, max_line_height=pdf.font_size, fill=True, align='C')

            pdf.ln(20)



            #
            # SESSION DETAILS TABLE
            #

            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(w=pdf.epw, txt=f'Managed Device Remote Control Session Details', align='L', ln=1)
            pdf.ln(5)

            pdf.set_fill_color(224, 102, 54)
            pdf.set_text_color(255,255,255)
            pdf.set_font('Helvetica', 'B', 9)
            line_height = pdf.font_size * 4
            col_width = pdf.epw / 6 # distribute content evenly as baseline

            pdf.multi_cell(col_width*1.25, line_height, 'Session Started', border='LTB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*1, line_height, 'Technician', border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*1, line_height, 'Device Name', border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*1, line_height, 'Device IP', border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*.5, line_height, 'Type', border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*1.25, line_height, 'Duration (h:mm:ss)', border='TBR', ln=1, max_line_height=pdf.font_size, fill=True, align='C')

            pdf.set_text_color(0,0,0)
            pdf.set_font('Helvetica', '', 7)
            line_height = pdf.font_size * 2
            for (idx,rec) in enumerate(consoles):
                if idx%2 == 0:
                    pdf.set_fill_color(252, 245, 233)
                else:
                    pdf.set_fill_color(249, 234, 213)

                if rec['resoruceId'] in resources:
                    resource = resources[rec['resoruceId']]
                else:
                    resource = {
                        "name": "<Removed device>",
                        "ipAddress": "-"
                    }
                pdf.multi_cell(col_width*1.25, line_height, rec['local_start_string'], border='LTB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
                pdf.multi_cell(col_width*1, line_height, f'{users[rec["userId"]]["firstName"]} {users[rec["userId"]]["lastName"]}', border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
                pdf.multi_cell(col_width*1, line_height, resource['name'], border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
                pdf.multi_cell(col_width*1, line_height, resource['ipAddress'], border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
                pdf.multi_cell(col_width*.5, line_height, rec["consoleProtocol"], border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
                pdf.multi_cell(col_width*1.25, line_height, str(rec['duration']), border='TBR', ln=1, max_line_height=pdf.font_size, fill=True, align='C')

        else:
            pdf.ln(60)
            pdf.cell(w=pdf.epw, txt="No Remote Control Sessions occurred in the reporting period", align='C')


        repdir = f'{outdir}{os.sep}{tenant["name"]}'
        if not os.path.exists(repdir):
            os.makedirs(repdir)
        pdf_file = "remote_control_usage_report.pdf"
        pdf.output(f'{repdir}{os.sep}{pdf_file}')

if __name__ == "__main__":
    # execute only if run as a script
    report() 