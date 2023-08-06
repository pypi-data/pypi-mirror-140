import opreport.helpers as helpers
from datetime import datetime, date, time
import os

def report(openv, tenants, daterange, outdir, logo):
    (start, end, bl_start, bl_end, utc_offset) = daterange

    today_beginning = datetime.combine(date.today(), time()) 
    offset =  "{}d".format((today_beginning.astimezone() - end).days)
    range = "{}d".format((end - start).days)
    for tenant in tenants:
        print("Tenant is " + tenant['uniqueId'] + " - " + tenant['name'])

        pdf = helpers.PDF_STD_HEADER_FOOTER(tenant, "Network Utilization Report", start, end, None, None, logo, 'P', 'mm', 'Letter')
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font('Helvetica', '', 14)

        helpers.top_n_timeseries_plus_detail_with_instance(
            openv, tenant, pdf,
            title="Cisco CPU Utilization Average (%)",
            metric="cisco_cpu_utilization",
            range=range,
            span="1h",
            offset=offset,
            n=10,
            fig_h=3,
            fig_w=8
            )


        pdf.add_page()

        helpers.top_n_timeseries_plus_detail_with_instance(
            openv, tenant, pdf,
            title="Cisco Memory Utilization Average (%)",
            metric="cisco_memory_pool_util_percent",
            range=range,
            span="1h",
            offset=offset,
            n=10,
            fig_h=3,
            fig_w=8
            )

        pdf.add_page()

        helpers.top_n_timeseries_plus_detail_with_instance(
            openv, tenant, pdf,
            title="Incoming Bandwidth Utilization Average (%)",
            metric="network_interface_utilization_in",
            range=range,
            span="1h",
            offset=offset,
            n=10,
            fig_h=3,
            fig_w=8
            )

        pdf.add_page()

        helpers.top_n_timeseries_plus_detail_with_instance(
            openv, tenant, pdf,
            title="Outgoing Bandwidth Utilization Average (%)",
            metric="network_interface_utilization_out",
            range=range,
            span="1h",
            offset=offset,
            n=10,
            fig_h=3,
            fig_w=8
            )



        repdir = f'{outdir}{os.sep}{tenant["name"]}'
        if not os.path.exists(repdir):
            os.makedirs(repdir)
        pdf_file = "network_utilization_report.pdf"
        pdf.output(f'{repdir}{os.sep}{pdf_file}')

if __name__ == "__main__":
    # execute only if run as a script
    report()