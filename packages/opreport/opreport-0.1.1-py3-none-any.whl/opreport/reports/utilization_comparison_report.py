from genericpath import exists
from fpdf import FPDF
from py import process
from opreport.opsramp import env, metrics, objects
import datetime
from dateutil.relativedelta import relativedelta
import sys
import json
import matplotlib.pyplot as plt
import  matplotlib.dates as mdates
#import numpy as np
import pandas as pd
import array
from functools import reduce
import os
import re
import opreport.helpers as helpers

class PDF(FPDF):
    def __init__(self, client, start, end, bl_start, bl_end, logo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource = {'name': 'none'}
        self.client = client
        self.start = start
        self.end = end
        self.bl_start = bl_start
        self.bl_end = bl_end
        self.logo = logo


    def header(self):
        #self.add_font('DejaVu Sans', '', 'fonts/DejaVuSans.ttf', uni=True)
        #self.add_font('DejaVu Sans Bold', '', 'fonts/DejaVuSans-Bold.ttf', uni=True)
        if self.page_no() == 1:
            self.image(self.logo, 10, 8, 40)
            # font
            self.set_font('DejaVu Sans Bold', '', 16)
            # Padding
            self.ln(15)
            # Title
            self.cell(30, 5, 'Utilization Comparison Report', border=False, ln=1, align='L')
            # Line break
            self.ln(5)
            self.set_font('DejaVu Sans Bold', '', 11)
            self.cell(40, 5, "Customer:")
            self.set_font('DejaVu Sans', '', 11)
            self.cell(40, 5, self.client['name'], ln=1)   
            self.set_font('DejaVu Sans Bold', '', 11)
            self.cell(40, 5, "Period:")
            self.set_font('DejaVu Sans', '', 11)
            self.cell(40, 5, self.start.strftime("%m/%d/%Y") + " - " + self.end.strftime("%m/%d/%Y") , ln=1)
            self.set_font('DejaVu Sans Bold', '', 11)
            self.cell(40, 5, "Baseline:")   
            self.set_font('DejaVu Sans', '', 11)
            self.cell(40, 5, self.bl_start.strftime("%m/%d/%Y") + " - " + self.bl_end.strftime("%m/%d/%Y") , ln=1)
            self.ln(5)
 
        self.set_fill_color(254,231,205)
        self.set_font('DejaVu Sans Bold', '', 10)

        if self.resource['name'] == 'none':
            self.cell(0, 5, "No matching devices for this client", fill=True, align='C')
        else:
            for attr in ['name', 'model', 'ipAddress', 'osName', 'aliasName']:
                if attr not in self.resource:
                    self.resource[attr] = "Unknown"

        self.resource['osName'] = re.sub(r' [.\d]+ Build.*','', self.resource['osName'])
        cwidth = self.epw/4
        cheight = 5
        fsize = 9
        self.set_font('DejaVu Sans Bold', '', fsize)
        self.cell(cwidth*.65, cheight, "Device Name:", fill=True, border='LT')
        self.set_font('DejaVu Sans', '', fsize)
        self.cell(cwidth*1, cheight, txt=self.resource['name'], ln=0, fill=True, border='T')
        self.set_font('DejaVu Sans Bold', '', fsize)
        self.cell(cwidth*.6, cheight, "Model:", fill=True, border='T')
        self.set_font('DejaVu Sans', '', fsize)
        self.cell(cwidth*1.75, cheight, txt=self.resource['model'], ln=1, fill=True, border='RT')

        self.set_font('DejaVu Sans Bold', '', fsize)
        self.cell(cwidth*.65, cheight, "IP:", fill=True, border='L')
        self.set_font('DejaVu Sans', '', fsize)
        self.cell(cwidth*1, cheight, txt=self.resource['ipAddress'], ln=0, fill=True, border='')
        self.set_font('DejaVu Sans Bold', '', fsize)
        self.cell(cwidth*.6, cheight, "OS:", fill=True, border='')
        self.set_font('DejaVu Sans', '', fsize)
        self.cell(cwidth*1.75, cheight, txt=self.resource['osName'], ln=1, fill=True, border='R')

        self.set_font('DejaVu Sans Bold', '', fsize)
        self.cell(cwidth*.65, cheight, "Alias:", fill=True, border='LB')
        self.set_font('DejaVu Sans', '', fsize)
        self.cell(cwidth*1, cheight, txt=self.resource['aliasName'], ln=0, fill=True, border='B')
        self.set_font('DejaVu Sans Bold', '', fsize)
        self.cell(cwidth*.6, cheight, "Warranty Exp.:", fill=True, border='B')
        self.set_font('DejaVu Sans', '', fsize)
        self.cell(cwidth*1.75, cheight, txt='', ln=1, fill=True, border='RB')


    # Page footer
    def footer(self):
        #self.add_font('DejaVu Sans', '', 'fonts/DejaVuSans.ttf', uni=True)
        # Set position of the footer
        self.set_y(-15)
        # set font
        self.set_font('DejaVu Sans', '', 7)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

def report(openv, tenants, daterange, outdir, logo):
    (start, end, bl_start, bl_end, utc_offset) = daterange

    images_per_line = 2
    for tenant in tenants:
        print("Tenant is " + tenant['uniqueId'] + " - " + tenant['name'])
        pdf = PDF(tenant, start, end, bl_start, bl_end, logo, 'P', 'mm', 'Letter')
        pdf.add_font('DejaVu Sans', '', 'fonts/DejaVuSans.ttf', uni=True)
        pdf.add_font('DejaVu Sans Bold', '', 'fonts/DejaVuSans-Bold.ttf', uni=True)

        # get total page numbers
        pdf.alias_nb_pages()

        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font('DejaVu Sans', '', 14)

        is_first_resource = True
        resources = objects.get_objects(openv, obtype='resources', tenant=tenant['uniqueId'], queryString='resourceType:Windows,Linux')
    
        rcount = 0
        rtotal = len(resources)
        print("Got " + str(rtotal) + " matching resources for tenant " + tenant['name'] + " before filtering for actives.")
        resources = list(filter(lambda r: ('status' in r and r['status'] == 'UP'), resources))
        rtotal = len(resources)
        print("After filtering device count is " + str(rtotal))
        if rtotal == 0:
            print("Skipping this client as there are 0 matching devies")
            continue
        for resource in resources:
            rcount +=1
            #if rcount > 5:
            #    break
            print("Processing resource " + str(rcount) + " of " + str(rtotal) + " - " + resource['name'])
            pdf.resource = resource
            pdf.add_page()

            images_this_line = 0
            current_y = pdf.get_y()

            aggregates = {}
            units = {}
            labels = {
                'system.cpu.usage.utilization': 'CPU Utilization',
                'system.disk.usage.utilization': 'Disk Utilization',
                'system.memory.usage.utilization': 'Memory Utilization',
                'system.disk.usage.freespace': 'Disk Free Space'
            }
            bl_avgs = {}
            metriclist = ['system.cpu.usage.utilization','system.disk.usage.utilization','system.memory.usage.utilization']
            #for metricname in ['system.cpu.usage.utilization','system.disk.usage.utilization','system.memory.usage.utilization', 'system.disk.usage.freespace'] :
            for (midx,metricname) in enumerate(metriclist) :
                aggregates[metricname] = {}
                print("  Metric: " + metricname)
                unit_label = ""
                dfs = []
                bl_dfs = []
                if images_this_line >= images_per_line:
                    images_this_line = 0
                else:
                    pdf.set_y(current_y)
                current_y = pdf.get_y()

                opmetrics = metrics.get_metricdatasets(openv,tenant['uniqueId'],resource['id'], metricname, int(start.timestamp()+utc_offset), int(end.timestamp()+utc_offset-1))
                bl_opmetrics = metrics.get_metricdatasets(openv,tenant['uniqueId'],resource['id'], metricname, int(bl_start.timestamp()+utc_offset), int(bl_end.timestamp()+utc_offset-1))
                if len(opmetrics) > 0  and 'message' not in opmetrics and 'data' in  opmetrics[0] and len(opmetrics[0]['data']) > 0 :
                    show_legend = True
                    if len(opmetrics) == 1:
                        show_legend = False

                    for instance in opmetrics:
                        if re.match(r'.*docker/overlay.*', instance['component']):
                            continue
                        units[metricname] = instance['unit']
                        unit_label = instance['unitLabel']
                        dfs.append(pd.DataFrame.from_dict(instance['data'], orient='index',columns=[instance['component']] ))

                    for bl_instance in bl_opmetrics:
                        if re.match(r'.*docker/overlay.*', bl_instance['component']):
                            continue
                        bl_dfs.append(pd.DataFrame.from_dict(bl_instance['data'], orient='index',columns=[bl_instance['component']] ))



                    df_merged = reduce(lambda  left,right: pd.concat([left,right],axis=1), dfs)
                    df_merged.index = pd.to_datetime(df_merged.index,unit='s')
                    df_merged = df_merged.sort_index()

                    bl_df_merged = reduce(lambda  left,right: pd.concat([left,right],axis=1), bl_dfs)
     
                    for col in df_merged.columns.to_list():
                        plt.plot_date(df_merged.index.to_pydatetime(), df_merged[col], fmt='-')
                    ax=plt.gca()
                    fig = ax.get_figure()
                    fig.subplots_adjust(bottom=0.2)
                    if show_legend:
                        fig.legend(df_merged.columns, loc="lower center", ncol=len(labels[metricname]), frameon=False)
                        #fig.legend(df_merged.columns, loc="lower center", ncol=len(labels[metricname]), bbox_to_anchor=(0.5, -1))
                    plt.title(labels[metricname])
                    plt.xticks(rotation = 45)
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
                    

                    aggregates[metricname]['min'] = df_merged.min(axis=0)
                    aggregates[metricname]['max'] = df_merged.max(axis=0)
                    aggregates[metricname]['mean'] = df_merged.mean(axis=0)
                    aggregates[metricname]['std'] = df_merged.std(axis=0)
                    bl_avgs[metricname] = bl_df_merged.mean(axis=0)

                    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                    ax.set_ylabel(unit_label)

                    imagefile = resource['id'] + "_" + metricname +'.png'
                    plt.savefig(imagefile)
                    plt.clf()
                    plt.close(fig)

                    #print(json.dumps(opmetrics, indent=2, sort_keys=False))
                    #sys.exit(0)

                    pdf.image(imagefile, w=pdf.epw/images_per_line, x=pdf.epw/images_per_line*images_this_line+10)
                    os.remove(imagefile)
                    images_this_line += 1
                else:
                    pdf.set_x(images_this_line*pdf.epw/images_per_line)
                    images_this_line += 1
                    if images_this_line == images_per_line :
                        ln =1
                    else:
                        ln = 0
                    pdf.set_font('DejaVu Sans Bold', '', 10)
                    pdf.set_x(pdf.get_x() + 15)
                    pdf.cell(txt="No data for " + metricname, w=pdf.epw/images_per_line-10, h=50, border=0, ln = ln, align='C')
                    if midx == len(metriclist) - 1:
                        pdf.ln(80)


            pdf.set_font("DejaVu Sans", size=7)
            line_height = pdf.font_size * 1.5
            col_width = pdf.epw / 5 # distribute content evenly

            pdf.ln(line_height)
            pdf.set_font('DejaVu Sans Bold', '', 7)
            pdf.set_fill_color(254,231,205)
            pdf.multi_cell(col_width*2, line_height*2, 'Details', border=1, ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*.5, line_height*2, 'Lowest', border=1, ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*.5, line_height*2, 'Highest', border=1, ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*.5, line_height*2, 'Average', border=1, ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*.5, line_height*2, 'Std. Dev.', border=1, ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*.5, line_height*2, 'Baseline Average', border=1, ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.multi_cell(col_width*.5, line_height*2, 'Differential', border=1, ln=3, max_line_height=pdf.font_size, fill=True, align='C')
            pdf.ln(line_height*2)
            pdf.set_font('DejaVu Sans', '', 7)
            for (metricname, aggs) in aggregates.items():
                if len(aggs) == 0:
                    continue
                num_components = len(aggs['max'])
                if num_components == 1:
                        pdf.multi_cell(col_width*2, line_height, labels[metricname], border=1, ln=3, max_line_height=pdf.font_size)
                        for (agg, vals) in aggs.items():
                                cellval = ""
                                if vals[0] is None:
                                    cellval = "-"
                                else:
                                    cellval = "{:.2f}".format(vals[0]) + units[metricname]
                                pdf.multi_cell(col_width*.5, line_height, cellval, border=1, ln=3, max_line_height=pdf.font_size, align='C')
                        baseavg = ""
                        differ = ""
                        trend = ""
                        differnum = None
                        if pd.isna(bl_avgs[metricname][0]) or bl_avgs[metricname][0] is None or aggs['mean'][0] is None:
                            baseavg = "-"
                            differ = "-"
                            trend = "-"
                        else:
                            baseavg = "{:.2f}".format(bl_avgs[metricname][0]) + units[metricname]
                            differ =  "{:.2f}".format(aggs['mean'][0] - bl_avgs[metricname][0]) + units[metricname]
                            differnum = aggs['mean'][0] - bl_avgs[metricname][0]
                        pdf.multi_cell(col_width*.5, line_height, baseavg, border=1, ln=3, max_line_height=pdf.font_size, align='C')
                        if differnum is not None and differnum > 0:
                            differ = "+" + differ + " \u25b2"
                            pdf.set_text_color(255,0,0)
                        elif differnum is not None and differnum < 0:
                            differ = differ + " \u25bc"
                            pdf.set_text_color(76,153,0)
                        pdf.multi_cell(col_width*.5, line_height, differ, border=1, ln=3, max_line_height=pdf.font_size, align='C')
                        pdf.set_text_color(0,0,0)
                        pdf.ln(line_height)
                elif num_components > 1:
                        for i in range(0,num_components):
                            comp = aggs['max'].keys()[i]
                            pdf.multi_cell(col_width*2, line_height, labels[metricname] + " (" + comp + ")", border=1, ln=3, max_line_height=pdf.font_size)
                            for (agg, vals) in aggs.items():
                                cellval = ""
                                if vals[comp] is None:
                                    cellval = "-"
                                else:
                                    cellval = "{:.2f}".format(vals[comp]) + units[metricname]
                                pdf.multi_cell(col_width*.5, line_height, cellval , border=1, ln=3, max_line_height=pdf.font_size, align='C')

                            baseavg = ""
                            differ = ""
                            trend = ""
                            differnum = None
                            if pd.isna(bl_avgs[metricname][comp]) or bl_avgs[metricname][comp] is None or aggs['mean'][comp] is None:
                                baseavg = "-"
                                differ = "-"
                                trend = "-"
                            else:
                                baseavg = "{:.2f}".format(bl_avgs[metricname][comp]) + units[metricname]
                                differnum = aggs['mean'][comp] - bl_avgs[metricname][comp]
                                differ =  "{:.2f}".format(differnum)
                            pdf.multi_cell(col_width*.5, line_height, baseavg, border=1, ln=3, max_line_height=pdf.font_size, align='C')
                            if differnum is not None and differnum > 0:
                                differ = "+" + differ + " \u25b2"
                                pdf.set_text_color(255,0,0)
                            elif differnum is not None and differnum < 0:
                                differ = differ + " \u25bc"
                                pdf.set_text_color(76,153,0)
                            pdf.multi_cell(col_width*.5, line_height, differ, border=1, ln=3, max_line_height=pdf.font_size, align='C')
                            pdf.set_text_color(0,0,0)
                            pdf.ln(line_height)

            print("Completed resource " + resource['name'])

        repdir = f'{outdir}{os.sep}{tenant["name"]}'
        if not os.path.exists(repdir):
            os.makedirs(repdir)
        pdf_file = "utilization_comparison_report.pdf"
        pdf.output(f'{repdir}{os.sep}{pdf_file}')

if __name__ == "__main__":
    # execute only if run as a script
    report()