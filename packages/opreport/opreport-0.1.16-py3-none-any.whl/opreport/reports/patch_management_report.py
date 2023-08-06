from genericpath import exists
from tkinter import N
from fpdf import FPDF
from opreport.opsramp import objects, patching
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
from functools import reduce
import os

class PDF(FPDF):
    def __init__(self, client, start, end, bl_start, bl_end, logo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        self.start = start
        self.end = end
        self.bl_start = bl_start
        self.bl_end = bl_end
        self.logo = logo


    def header(self):
        logo_width = 25
        self.image(self.logo, 10, 8, h=13)
        self.set_font('Helvetica', 'B', 12)
        self.cell(w=self.epw, txt=self.client['name'], align='R', ln=1)
        self.ln(5)
        x = self.get_x()
        y = self.get_y()
        self.set_line_width(.5)
        self.line(x, y, self.epw+10, y)


        """
        self.set_font('Helvetica', 'B', 11)
        self.cell(40, 5, "Baseline:")   
        self.set_font('Helvetica', '', 11)
        self.cell(40, 5, self.bl_start.strftime("%m/%d/%Y") + " - " + self.bl_end.strftime("%m/%d/%Y") , ln=1)
        """

        self.ln(5)
 
        self.set_fill_color(254,231,205)
        self.set_font('Helvetica', 'B', 1)



    # Page footer
    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font('Helvetica', '', 7)
            self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

def report(openv, tenants, daterange, outdir, logo):
    (start, end, bl_start, bl_end, utc_offset) = daterange
    for (tnum,tenant) in enumerate(tenants):
        #if tnum > 1:
        #    continue
        indexes = []
        data = []
        print(f'Start processing tenant {tenant["uniqueId"]} - {tenant["name"]}')
        resources = objects.get_objects(openv, obtype='resources', tenant=tenant['uniqueId'], queryString='agentInstalled:true+resourceType:Windows,Linux')
        resources = list(filter(lambda r: ('status' in r and r['status'] == 'UP'), resources))
        if len(resources) == 0:
            print("Skipping tenant as there are no Windows/Linux agent-installed resources.")
            continue
        resources_by_id = {}
        for resource in resources:
            resources_by_id[resource['id']] = resource
        all_patches = pd.DataFrame(pd.json_normalize(patching.get_patches_on_resources(openv, tenant['uniqueId'])))
        count_needs_updates = 0
        
        missing_patches = pd.DataFrame()
        if len(all_patches) > 0:
            all_patches['resource.state'] = all_patches.apply(lambda row: resources_by_id[row['resource.id']]['state'] if row['resource.id'] in resources_by_id else 'MISSING', axis=1)
            all_patches['resource.status'] = all_patches.apply(lambda row: resources_by_id[row['resource.id']]['status'] if row['resource.id'] in resources_by_id else 'MISSING', axis=1)
            missing_patches = all_patches[(all_patches['resource.status'] == 'UP') & (all_patches['patchStatus'] == 'MISSING')]
            count_needs_updates = missing_patches.groupby('resource.id')['resource.id'].nunique().count()

        count_current = len(resources) - count_needs_updates
        pct_compliance = "N/A"
        if len(resources) > 0:
            pct_complete = f'{int(count_current/len(resources)*100)}%'


        count = [count_current, count_needs_updates]
        labels = ['Current', 'Needs Updates']
        plt.bar(labels, count, color=['#4590f7','#ea3323'])
        
        ax=plt.gca()
        ax.set_ylabel("Device Count")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis='y')
        fig = ax.get_figure()
        fig.suptitle('Device Update Status', fontsize=24)
        plt.xticks(fontsize=16)
        plt.ylabel('Device Count', fontsize=16)
        imagefile = f'{tenant["uniqueId"]}_patch_device_update_status.png'
        plt.savefig(imagefile)
        plt.clf()
        plt.close('all')

        #print(json.dumps(opmetrics, indent=2, sort_keys=False))
        #sys.exit(0)
        pdf = PDF(tenant, start, end, bl_start, bl_end, logo, 'P', 'mm', 'Letter')

        # get total page numbers
        pdf.alias_nb_pages()

        #
        # COVER PAGE
        #
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 25)
        titlewidth = 170
        pdf.set_y(pdf.eph/3)

        pdf.cell(w=pdf.epw, txt='MONTHLY PATCH', align='C', ln=1)
        pdf.cell(w=pdf.epw, txt='MANAGEMENT REPORT', align='C', ln=1)
        pdf.ln(60)
        
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(w=pdf.epw, txt=tenant['name'], align='C', ln=1)   
        pdf.ln(10)

        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(w=pdf.epw,txt="For the period:", align='C', ln=1)
        pdf.ln(5)
        pdf.cell(w=pdf.epw, txt=start.strftime("%m/%d/%Y") + " - " + end.strftime("%m/%d/%Y"), align='C', ln=1) 

        #
        # PIE CHART AND PCT
        #
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font('Helvetica', '', 14)
        pdf.image(imagefile, w=pdf.epw/2, x=0)
        os.remove(imagefile)
        pdf.set_xy(pdf.epw/2, 26)
        pdf.cell(w=pdf.epw/2, txt="Devices That Are Up To Date", align='C', ln=1)
        pdf.ln(20)
        pdf.set_x(pdf.epw/2)
        pdf.set_font('Helvetica', '', 70)
        pdf.cell(w=pdf.epw/2, txt=pct_complete, align='C', ln=1)

        #
        # DEVICES MISSING REQUIRED PATCHES
        #

        cell_height = 6
        pdf.cell(w=pdf.epw, txt="", ln=1)
        pdf.ln(20)
        pdf.set_font('Helvetica', 'B', 13)
        pdf.cell(w=pdf.epw, txt="Devices Missing Required Patches", align='L', ln=1)
        pdf.ln(5)
        missing_per_server = missing_patches.groupby(['resource.name', 'resource.resourceType'])['resource.name'].count() if len(missing_patches)>0 else {}
        pdf.set_font('Helvetica', 'B', 11)
        col_headers = ['Device Name', 'System Type', 'Total Missing', 'Category']
        for (idx,col_header) in enumerate(col_headers):
            ln = 1 if idx == len(col_headers)-1 else 3
            align = 'C' if col_header=='Totel Missing' else 'L'
            pdf.multi_cell(w=pdf.epw/len(col_headers), h=cell_height, txt=col_header, align=align, border='B', ln=ln)  
        pdf.set_font('Helvetica', '', 11)     
        for (grp, val) in missing_per_server.items():           
            pdf.multi_cell(w=pdf.epw/len(col_headers), h=cell_height, txt=grp[0], align='L', border='TB', ln=3)
            pdf.multi_cell(w=pdf.epw/len(col_headers), h=cell_height, txt=grp[1], align='L', border='TB', ln=3)
            pdf.multi_cell(w=pdf.epw/len(col_headers), h=cell_height, txt=str(val), align='C', border='TB', ln=3)
            pdf.multi_cell(w=pdf.epw/len(col_headers), h=cell_height, txt="Security Updates", align='L', border='TB', ln=1)

        
        #
        # PATCH INSTALLATION SUMMARY
        #

        pdf.add_page()
        pdf.set_fill_color(38,68,121)
        pdf.set_text_color(255,255,255)
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(w=pdf.epw, txt="Patch Installation Summary", align='L', ln=1, fill=True)
        pdf.ln(5)

        installed_patches = []
        if len(all_patches) > 0:
            all_patches['installedTime'] = pd.to_datetime(all_patches['installedTime'], infer_datetime_format=True)
            installed_patches = all_patches[(all_patches['patchStatus'] == 'INSTALLED') & (pd.notnull(all_patches['installedTime']))]
            installed_patches = installed_patches[(pd.to_datetime(installed_patches['installedTime']).dt.date>=start.date()) & (pd.to_datetime(installed_patches['installedTime']).dt.date<end.date())]
            print(f'Number of installed patches = {len(installed_patches)}')
            if len(installed_patches) > 0:
                sumlines = {}
                sumlines["Total Windows Patches Installed"] = len(installed_patches[(installed_patches['resource.resourceType']=='Windows')].groupby(['patch.id'])['patch.id'])
                sumlines["Total Linux Patches Installed"] = len(installed_patches[(installed_patches['resource.resourceType']=='Linux')].groupby(['patch.id'])['patch.id'])
                sumlines["Total Patches Installed"] = sumlines["Total Windows Patches Installed"] + sumlines["Total Linux Patches Installed"]

                sumlines["Total Windows Systems Patched"] = len(installed_patches[(installed_patches['resource.resourceType']=='Windows')].groupby(['resource.id'])['resource.id'])
                sumlines["Total Linux Systems Patched"]  = len(installed_patches[(installed_patches['resource.resourceType']=='Linux')].groupby(['resource.id'])['resource.id'])
                sumlines["Total Systems Patched"]  = sumlines["Total Windows Systems Patched"]  + sumlines["Total Linux Systems Patched"]

                sumlines["Total Patches Failed"] = 0
                sumlines["Total Patches Declined"] = 0

                patchtypes=installed_patches.groupby(['patch.category','patch.id']).size().groupby('patch.category').count()
                total = sum(patchtypes)
                patchtypes.plot.pie(labels=None, autopct=lambda s: str(round(s * total / 100)))
                ax=plt.gca()
                ax.set_ylabel(None)
                fig = ax.get_figure()
                fig.subplots_adjust(bottom=0.2)
                fig.suptitle('Patch Installation by Category', fontsize=17, fontname="Helvetica", fontweight="bold")
                plt.legend(patchtypes.index, loc="lower center", frameon=False, bbox_to_anchor=(0.5,-.2))
                imagefile = f'{tenant["uniqueId"]}_patch_types.png'
                plt.savefig(imagefile)
                plt.clf()
                plt.close('all')

                pdf.set_text_color(0,0,0)
                pdf.set_font('Helvetica', '', 12)
                pdf.cell(w=pdf.epw/2, txt="Patch Installation Summary", align='C', ln=1)
                pdf.ln(5)
                topy = pdf.get_y()
                pdf.set_font('Helvetica', '', 10)
                cell_height = 6
                for (name, val) in sumlines.items():
                    w_name = pdf.get_string_width(name)
                    w_val = pdf.epw/2-w_name-12
                    border = 'B'
                    if name == 'Total Patches Declined':
                        border = 'T'
                    pdf.cell(w=w_name, h=cell_height, txt=name, align='L', ln=0, border=border)
                    pdf.cell(w=w_val, h=cell_height, txt=str(val), align='R', ln=1, border=border)
                bottomy = pdf.get_y()
                pdf.image(imagefile, x=pdf.epw/2, y=topy-10, w=pdf.epw/2+10)
                os.remove(imagefile)
                pdf.ln(50)
                pdf.set_font('Helvetica', '', 12)
                pdf.cell(w=pdf.epw, txt="No Declined Patches During Report Period", align='C', ln=1)
                pdf.ln(20)
                pdf.set_font('Helvetica', '', 12)
                pdf.cell(w=pdf.epw, txt="No Failed Patch Installations During Report Period", align='C', ln=1)


        if len(installed_patches) == 0:
                pdf.set_text_color(0,0,0)
                pdf.set_font('Helvetica', '', 12)
                pdf.cell(w=pdf.epw, txt="No Patches Installed During Report Period", align='C', ln=1)            

        print(f'Done processing tenant {tenant["uniqueId"]} - {tenant["name"]}')

        repdir = f'{outdir}{os.sep}{tenant["name"]}'
        if not os.path.exists(repdir):
            os.makedirs(repdir)
        pdf_file = "patch_management_report.pdf"
        pdf.output(f'{repdir}{os.sep}{pdf_file}')


if __name__ == "__main__":
    # execute only if run as a script
    report()