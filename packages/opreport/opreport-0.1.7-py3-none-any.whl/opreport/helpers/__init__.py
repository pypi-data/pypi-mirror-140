from attr import has
from fpdf import FPDF
from opreport.opsramp import metrics
import matplotlib.pyplot as plt
import  matplotlib.dates as mdates
import pandas as pd
import os
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


class PDF_STD_HEADER_FOOTER(FPDF):
    def __init__(self, tenant, title, start, end, bl_start=None, bl_end=None, logo_file='logo.jpeg', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource = {'name': 'none'}
        self.tenant = tenant
        self.start = start
        self.end = end
        self.bl_start = bl_start
        self.bl_end = bl_end
        self.title = title
        self.logo_file = logo_file


    def header(self):
        if self.page_no() == 1:
            self.image(self.logo_file, 10, 8, h=13)
            self.set_font('Helvetica', 'B', 16)
            self.ln(15)
            self.cell(30, 5, self.title, border=False, ln=1, align='L')
            self.ln(5)
            self.set_font('Helvetica', 'B', 11)
            self.cell(40, 5, "Customer:")
            self.set_font('Helvetica', '', 11)
            self.cell(40, 5, self.tenant['name'], ln=1)   
            self.set_font('Helvetica', 'B', 11)
            self.cell(40, 5, "Period:")
            self.set_font('Helvetica', '', 11)
            self.cell(40, 5, self.start.strftime("%m/%d/%Y") + " - " + self.end.strftime("%m/%d/%Y") , ln=1)

            if self.bl_start is not None and self.bl_end is not None:
                self.set_font('Helvetica', 'B', 11)
                self.cell(40, 5, "Baseline:")   
                self.set_font('Helvetica', '', 11)
                self.cell(40, 5, self.bl_start.strftime("%m/%d/%Y") + " - " + self.bl_end.strftime("%m/%d/%Y") , ln=1)

            self.ln(5)
        else:
            logo_width = 25
            self.image(self.logo_file, 10, 8, h=9)
            self.set_font('Helvetica', 'B', 12)
            self.cell(w=self.epw, txt=self.tenant['name'], align='R', ln=1)
            self.ln(5)
            x = self.get_x()
            y = self.get_y()
            self.set_line_width(.5)
            self.line(x, y, self.epw+10, y)
            self.ln(5)

    # Page footer
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 7)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

def top_n_timeseries_plus_detail_with_instance(openv, tenant, pdf, title, metric, range, span, offset=None, n=10, top_aggtype='avg', fig_h=3, fig_w=8, dpi=600, show_chart=True, show_details=True, all_details=True):
    if offset is None:
        offsetstring = ""
    else:
        offsetstring = f' offset {offset}'
    search = f'topk({n},{top_aggtype}_over_time({metric}[{range}:{span}]{offsetstring}))'
    top_n = metrics.promql_instance_search(openv, tenant['uniqueId'], search)
    labels = []
    labelmatch = ""
    for (idx,instance) in enumerate(top_n):
        if idx > 0:
            labelmatch += '|'
        labelmatch += instance['metric']['uuid']
        labels.append(instance['metric']['name'])
    
    if (show_chart):
        search = f'{metric}{{uuid=~"{labelmatch}"}}[{range}:{span}]{offsetstring}'
        data = metrics.promql_instance_search(openv, tenant['uniqueId'], search)
        df = []
        for (idx,topn) in enumerate(top_n):
            for (idx2, row) in enumerate(data):
                if topn['metric']['name'] == row['metric']['name'] and topn['metric']['instance'] == row['metric']['instance']:
                    device_name = row['metric']['name']
                    instance_name = row['metric']['instance']
                    colname = device_name + " (" + instance_name + ")"
                    dfpart = pd.DataFrame(row['values'], columns=['timestamp', colname])
                    dfpart[colname] = pd.to_numeric(dfpart[colname])
                    if idx == 0:
                        df = dfpart
                    else:
                        df = pd.merge(df, dfpart, on='timestamp', how='outer')
        if len(df) > 0:
            df=df.set_index('timestamp')
            #df = pd.merge(pd.DataFrame(index=(pd.date_range(pdf.start,pdf.end).astype(int)/1000000000).astype(int)[:-1]),df, how='outer', left_index=True, right_index=True)
            df = df.sort_index()
            plt.figure(figsize=(fig_w,fig_h), dpi=dpi)
            for col in df.columns.to_list():
                plt.plot_date(mdates.epoch2num(df.index), df[col], fmt='-')
            ax=plt.gca()
            fig = ax.get_figure()
            fig.subplots_adjust(bottom=0.28)
            fig.legend(df.columns, loc="lower center", ncol=4, frameon=False, fontsize=6)

            plt.title(f'Top {str(n)} {title}', fontsize=9, fontweight='bold')
            plt.xticks(rotation = 45, fontsize=6)
            plt.yticks(fontsize=7)
            #ax.set_xlim([mdates.epoch2num(df.index[0]), mdates.epoch2num(df.index[-1])])
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            ax.grid(axis='y')
            imagefile = f'{tenant["uniqueId"]}_{metric}.png'
            plt.savefig(imagefile, bbox_inches='tight')
            plt.clf()
            plt.close(fig)
            pdf.image(imagefile, x=pdf.l_margin, w=pdf.epw)
            os.remove(imagefile)

    pdf.ln(8)

    pdf.set_text_color(0,0,0)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(w=pdf.epw, txt=f'{title} Statistics', align='L', ln=1)
    pdf.ln(5)

    if (show_details):
        details = {}
        aggs = ['avg', 'min', 'max']
        for (agg_idx,agg) in enumerate(aggs):
            search = f'sort_desc({agg}_over_time({metric}[{range}:{span}]{offsetstring}))'
            data = metrics.promql_instance_search(openv, tenant['uniqueId'], search)
            for row in data:
                device_name = row['metric']['name']
                instance_name = row['metric']['instance']
                colname = device_name + " (" + instance_name + ")"
                if agg_idx == 0:
                    details[colname] = {}
                details[colname][agg] = float(row['value'][1])

 
        pdf.set_fill_color(224, 102, 54)
        pdf.set_text_color(255,255,255)
        pdf.set_font('Helvetica', 'B', 9)
        line_height = pdf.font_size * 2
        col_width = pdf.epw / 4 # distribute content evenly as baseline

        pdf.multi_cell(col_width*2.5, line_height, 'Device', border='LTB', ln=3, max_line_height=pdf.font_size, fill=True, align='L')
        pdf.multi_cell(col_width*.5, line_height, 'Minimum', border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
        pdf.multi_cell(col_width*.5, line_height, 'Maximum', border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
        pdf.multi_cell(col_width*.5, line_height, 'Average', border='TBR', ln=1, max_line_height=pdf.font_size, fill=True, align='C')

        pdf.set_text_color(0,0,0)
        pdf.set_font('Helvetica', '', 7)
        line_height = pdf.font_size * 2
        for idx, (col_name, aggs) in enumerate(details.items()):
            if idx%2 == 0:
                pdf.set_fill_color(252, 245, 233)
            else:
                pdf.set_fill_color(249, 234, 213)
            pdf.multi_cell(col_width*2.5, line_height, col_name, border='LTB', ln=3, max_line_height=pdf.font_size, fill=True, align='L')
            pdf.multi_cell(col_width*.5, line_height, "{:.2f}".format(aggs['min']), border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*.5, line_height, "{:.2f}".format(aggs['max']), border='TB', ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*.5, line_height, "{:.2f}".format(aggs['avg']), border='TBR', ln=1, max_line_height=pdf.font_size, fill=True, align='C')          


def compute_dates(args):
    start = args.start
    end = args.end

    if start is None:
        start = datetime.today().astimezone()
        if start.month == 1 :
            start = start.replace(year=start.year-1, month=12, day=1,hour=0,minute=0,second=0,microsecond=0)
        else: 
            start = start.replace(month=start.month-1, day=1,hour=0,minute=0,second=0,microsecond=0)
    else:
        start = datetime.strptime(start,"%Y-%m-%d").astimezone()

    if end is None:
        if start.month == 12 :
            end = start.replace(year=start.year+1, month=1)
        else: 
            end = start.replace(month=start.month+1)
    else:
        end = datetime.strptime(end,"%Y-%m-%d").astimezone()

    ts = time.time()
    utc_offset = int((datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)).total_seconds())


    if hasattr(args, 'baseline_months_back'):
        bl_start = None
        bl_end = None
        baseline_months_back = args.baseline_months_back
        if baseline_months_back is None:
            baseline_months_back = 1
        bl_start = start + relativedelta(months=-baseline_months_back)
        bl_end = end + relativedelta(months=-baseline_months_back)
        return (start, end, bl_start, bl_end, utc_offset)
    else:
        return (start, end, None, None, utc_offset)