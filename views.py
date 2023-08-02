import configparser
import datetime
import os
import pandas as pd
import psycopg2
from django.http import HttpResponse
from django.http.response import HttpResponse
from django.shortcuts import render
import mimetypes


def download_file(request):
    # Define Django project base directory
    # Define text file name
    filepath = 'test.txt'
    # Define the full file path
    # Open the file for reading content
    path = open(filepath, 'r')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filepath
    # Return the response value
    return response


# Create your views here.
def home(request):
    obj = GetCount()
    week_individual_df, team_df, monthly_df = obj.get()
    week_individual_df.index += 1
    team_df.index += 1
    monthly_df.index += 1
    today = datetime.date.today()
    idx = (today.weekday() + 1) % 7 + 1
    sat = today - datetime.timedelta(7 + idx - 6)
    saturday = sat.strftime('%b %d, %Y')
    today = today.strftime('%b %d, %Y')
    html = '<a href="/status">Check Status</a><br><a href="/qc_individual">Qc Weekly Individual</a> '
    html += '<br><a href="/qc_team">Qc Team Count</a>'
    html += '<br><a href="/qc_monthly">Qc Monthly Count</a>'
    html += '<br><a href="/unassigned_files">Un-Assigned Files</a>'
    html += f'<h2>Week Count - {saturday} - {today}</h2><br>'
    html += week_individual_df.to_html()
    html += f'<h2>Team Week Count - {saturday} - {today}</h2><br>'
    html += team_df.to_html()
    month = datetime.datetime.today().strftime('%B, %Y')
    html += f'<h2>Monthly Individual Count - {month}</h2><br>'
    html += monthly_df.to_html()

    return HttpResponse(html)


def home_1(request):
    return render(request, 'Sidebar_Home.html')


def home_2(request):
    return render(request, 'Image_Home_Bars.html')


def get_tool_status(request):
    obj = GetCount()
    df = obj.tool_count()
    return HttpResponse(df)


def get_qc_list_view(request):
    obj = GetCount()
    df = obj.qc_status_list_view()

    return render(request, 'Qc_Status.html', {'df': df})


def qc_individual_count(request):
    obj = GetCount()
    week_individual_df = obj.qc_individual()

    return render(request, 'Individual_Count_QC.html',
                  {'week_individual_df': week_individual_df})


def dev_individual_count(request):
    obj = GetCount()
    dev_individual = obj.dev_individual()

    return render(request, 'Individual_Count_Dev.html',
                  {'dev_individual': dev_individual})


def jr_dev_individual_count(request):
    obj = GetCount()
    dev_individual = obj.jr_dev_individual()

    return render(request, 'Individual_Count_jrdev.html',
                  {'dev_individual': dev_individual})


def qc_team_count(request):
    obj = GetCount()
    team_df = obj.qc_team()

    return render(request, 'Qc_Team.html', {'team_df': team_df})


def dev_team_count(request):
    obj = GetCount()
    team_df = obj.dev_team()

    return render(request, 'Dev_Team.html', {'team_df': team_df})


def qc_month_count(request):
    obj = GetCount()
    month_qc = obj.monthly_qc()

    return render(request, 'Qc_Monthly_Count.html', {'month_qc': month_qc})


def get_files(request):
    obj = GetCount()
    file_unassigned, columns = obj.get_files()

    return render(request, 'Un_Assigned_Files_v3.html',
                  {'file_unassigned': file_unassigned, 'columns': columns})


def sample(request):
    obj = GetCount()
    week_individual_df, team_df, monthly_df = obj.test()

    return render(request, 'test.html', {'week_individual_df': week_individual_df,
                                         'team_df': team_df,
                                         'monthly_df': monthly_df})


class GetCount:
    def __init__(self, year=2022):
        self.config_file_name = r'D:\Display Count\configfile_automation.ini'
        self.con = self.create_connection()
        self.cur = self.con.cursor()
        self.df = None
        self.year = year
        # self.receiver = 'Shanmugapradeep.Jayavel@prism.science'

    def fetch_credentials(self):
        config_obj = configparser.ConfigParser()
        config_obj.read(self.config_file_name)
        dbparam = config_obj["postgresql"]
        user = dbparam["user"]
        password = dbparam["password"]
        host = dbparam["host"]
        port = int(dbparam["port"])
        dbase = dbparam["db"]
        return user, password, host, port, dbase

    def create_connection(self):
        user, password, host, port, dbase = self.fetch_credentials()
        con = psycopg2.connect(host=host, database=dbase, user=user, port=port,
                               password=password)
        return con

    def get(self):
        if self.con.closed:
            self.con = self.create_connection()
            self.cur = self.con.cursor()
        print('Processing the AE_abstracts Records Data...!')
        group_by_actual_query = f"""select qc_person,count(qc_person)  ,sum(abstract_count)  from indiatools.tbl_event_status tes where qc_completed_date  between
        current_date - extract(day from current_date)::int and current_date group by 1 order by 3 desc """
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        data_dict = []
        for n, master_value in enumerate(group_values, start=1):
            data_dict.append({'Name': master_value[0],
                              'Count': master_value[1],
                              'Abstracts': master_value[2]})
        monthly_df = pd.DataFrame(data_dict)

        group_by_actual_query = f"""select * from
(SELECT 'The Unstoppable' as team_name,count(abstract_count),sum(abstract_count)
FROM indiatools.tbl_event_status tes
where qc_completed_date between current_date - extract(isodow from current_date)::int and current_date
and qc_person in ('Vinoth Kumar','Dharani R','Kaviarasu P','Chithra P','Bruntha Devi')
group by 1 order by 3 desc) as t1
union
select * from
(SELECT 'Flaming Warriors',count(abstract_count),sum(abstract_count)
FROM indiatools.tbl_event_status tes
where qc_completed_date between current_date - extract(isodow from current_date)::int and current_date
and qc_person in ('Shanmugapriya J','Lakshmanakumar M','Saravanakumar K','Vimal R','Sundarraj M')
group by 1 order by 3 desc) as t2
union
select * from
(SELECT 'Fantastic Four' as team_name,count(abstract_count),sum(abstract_count)
FROM indiatools.tbl_event_status tes
where qc_completed_date between current_date - extract(isodow from current_date)::int and current_date
and qc_person in ('Sowbarnika K J','Anisha V','Nivetha S','Karthikeyan M','Kalaiyarasi R')
group by 1 order by 3 desc) as t3 order by 3 desc"""
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        data_dict = []
        for n, master_value in enumerate(group_values, start=1):
            data_dict.append({'Team': master_value[0],
                              'Count': master_value[1],
                              'Abstracts': master_value[2]})
        team_df = pd.DataFrame(data_dict)

        group_by_actual_query = f"""select qc_person,count(qc_person)  ,sum(abstract_count)  from indiatools.tbl_event_status tes where qc_completed_date  between
                                current_date - extract(isodow from current_date)::int and current_date group by 1 order by 3 desc """
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        data_dict = []
        for n, master_value in enumerate(group_values, start=1):
            data_dict.append({'Name': master_value[0],
                              'Count': master_value[1],
                              'Abstracts': master_value[2]})
        week_individual_df = pd.DataFrame(data_dict)

        self.con.close()
        return week_individual_df, team_df, monthly_df

    def tool_count(self):
        if self.con.closed:
            self.con = self.create_connection()
            self.cur = self.con.cursor()
        group_by_actual_query = f"""select qc_person ,tsm.file_status ,abstract_count ,programmer_name  from indiatools.tbl_event_status tes
        left join indiatools.tbl_status_master tsm on tsm.id = tes.status
        where tes.status in (5,6,7,9) order by tsm.id"""
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        data_dict = {}
        for n, master_value in enumerate(group_values, start=1):
            qc_name = master_value[0]
            dict_values = {'Name': master_value[0],
                           'Status': master_value[1],
                           'Abstract Count': master_value[2],
                           'Programmer Name': master_value[3]}
            if data_dict.get(qc_name):
                data_dict[qc_name].append(dict_values)
            else:
                data_dict[qc_name] = [dict_values]
        html = '<a href="/home">Home</a><br><br><br>'

        n = 1
        for value in data_dict.values():
            df = pd.DataFrame(value)
            df.index += 1
            if n % 2 != 0:
                require_html = f'<div style="float:left">{df.to_html()}</div><br><br>'.replace(
                    '<th>', '<th style="text-align: center;">')
            else:
                require_html = f'<div style="float:right">{df.to_html()}</div><br><br>'.replace(
                    '<th>', '<th style="text-align: center;">')
            n += 1
            html += require_html
        self.con.close()

        return html

    def qc_status_list_view(self):
        if self.con.closed:
            self.con = self.create_connection()
            self.cur = self.con.cursor()
        group_by_actual_query = f"""select qc_person ,tsm.file_status ,abstract_count ,programmer_name,prism_id  from indiatools.tbl_event_status tes
        left join indiatools.tbl_status_master tsm on tsm.id = tes.status
        where tes.status in (5,6,7,9) order by 3 desc"""
        self.cur.execute(group_by_actual_query)
        group_values = [list(_) for _ in self.cur.fetchall()]
        self.con.close()
        return group_values

    def get_files(self):
        if self.con.closed:
            self.con = self.create_connection()
            self.cur = self.con.cursor()
        group_by_actual_query = f"""select abstract_type, programmer_name, abstract_count ,programmer_comments, jrdevname ,jrdevcomments ,prism_id , tn.eventname, tn.eventyear,tn.startdate ,tn.enddate,tn.abstracturl
from indiatools.tbl_event_status tes
left join tblevent_new tn on tn.prismid = tes.prism_id
where tes.status = 4 and (qc_person is null or qc_person = 'Not Assigned')
order by 3 desc"""
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        columns = ['abstract_type', 'programmer_name', 'abstract_count',
                   'programmer_comments', 'jrdevname', 'jrdevcomments', 'prism_id',
                   'eventname', 'eventyear', 'startdate', 'enddate', 'abstracturl']
        self.con.close()
        return group_values, columns

    def qc_individual(self):
        if self.con.closed:
            self.con = self.create_connection()
            self.cur = self.con.cursor()
        print('Processing the AE_abstracts Records Data...!')
        group_by_actual_query = f"""select qc_person,count(qc_person)  ,sum(abstract_count)  from indiatools.tbl_event_status tes where qc_completed_date  between
                                current_date - extract(isodow from current_date)::int and current_date group by 1 order by 3 desc """
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        self.con.close()
        return group_values

    def dev_individual(self):
        if self.con.closed:
            self.con = self.create_connection()
            self.cur = self.con.cursor()
        group_by_actual_query = f"""select programmer_name  ,count(*),sum(abstract_count)  from indiatools.tbl_event_status tes where completed_date  between
        current_date - extract(isodow from current_date)::int and current_date group by 1 order by 2 desc"""
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        self.con.close()
        return group_values

    def jr_dev_individual(self):
        if self.con.closed:
            self.con = self.create_connection()
            self.cur = self.con.cursor()
        group_by_actual_query = f"""select jrdevname  ,count(*),sum(abstract_count)  from indiatools.tbl_event_status tes where jrdevcompleteddate between
current_date - extract(isodow from current_date)::int and current_date group by 1 order by 2 desc"""
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        self.con.close()
        return group_values

    def qc_team(self):
        if self.con.closed:
            self.con = self.create_connection()
            self.cur = self.con.cursor()
        group_by_actual_query = f"""select * from
        (SELECT 'The Unstoppable' as team_name,count(abstract_count),sum(abstract_count)
        FROM indiatools.tbl_event_status tes
        where qc_completed_date between current_date - extract(isodow from current_date)::int and current_date
        and qc_person in ('Vinoth Kumar','Dharani R','Kaviarasu P','Chithra P','Bruntha Devi')
        group by 1 order by 3 desc) as t1
        union
        select * from
        (SELECT 'Flaming Warriors',count(abstract_count),sum(abstract_count)
        FROM indiatools.tbl_event_status tes
        where qc_completed_date between current_date - extract(isodow from current_date)::int and current_date
        and qc_person in ('Shanmugapriya J','Lakshmanakumar M','Saravanakumar K','Vimal R','Sundarraj M')
        group by 1 order by 3 desc) as t2
        union
        select * from
        (SELECT 'Fantastic Four' as team_name,count(abstract_count),sum(abstract_count)
        FROM indiatools.tbl_event_status tes
        where qc_completed_date between current_date - extract(isodow from current_date)::int and current_date
        and qc_person in ('Sowbarnika K J','Anisha V','Nivetha S','Karthikeyan M','Kalaiyarasi R')
        group by 1 order by 3 desc) as t3 order by 3 desc"""
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        self.con.close()
        return group_values

    def dev_team(self):
        if self.con.closed:
            self.con = self.create_connection()
            self.cur = self.con.cursor()
        group_by_actual_query = f"""select * from
(select 'Phoenix Star',count(abstract_count),sum(abstract_count)  from indiatools.tbl_event_status tes
where completed_date between current_date - extract(isodow from current_date)::int and current_date
and programmer_name in ('Archana A','Tamil Selvan','Jegathish E','Rajaraman S')) as t1
union
select * from
(select 'The Mavericks',count(abstract_count),sum(abstract_count)  from indiatools.tbl_event_status tes
where completed_date between current_date - extract(isodow from current_date)::int and current_date
and programmer_name in ('Sathishkumar G','Sarankumar N','Prasanth N')) as t2
union
select * from
(select 'BLS Developer',count(abstract_count),sum(abstract_count)  from indiatools.tbl_event_status tes
where completed_date between current_date - extract(isodow from current_date)::int and current_date
and programmer_name in ('Ashika R','Gangadharan N','Gowtham V')) as t3
union
select * from
(select 'Scraping Shadows',count(abstract_count),sum(abstract_count)  from indiatools.tbl_event_status tes
where completed_date between current_date - extract(isodow from current_date)::int and current_date
and programmer_name in ('Murugesan M','Siva A','Ragulvasanth A','Easwaramoorthy M')) as t4 order by 2 desc """
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        self.con.close()
        return group_values

    def monthly_qc(self):
        if self.con.closed:
            self.con = self.create_connection()
            self.cur = self.con.cursor()
        print('Processing the AE_abstracts Records Data...!')
        group_by_actual_query = f"""select qc_person,count(qc_person)  ,sum(abstract_count)  from indiatools.tbl_event_status tes where qc_completed_date  between
        current_date - extract(day from current_date)::int and current_date group by 1 order by 3 desc """
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        self.con.close()
        return group_values

    def test(self):
        if self.con.closed:
            self.con = self.create_connection()
            self.cur = self.con.cursor()
        print('Processing the AE_abstracts Records Data...!')
        group_by_actual_query = f"""select qc_person,count(qc_person)  ,sum(abstract_count)  from indiatools.tbl_event_status tes where qc_completed_date  between
        current_date - extract(day from current_date)::int and current_date group by 1 order by 3 desc """
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        # data_dict = []
        # for n, master_value in enumerate(group_values, start=1):
        #     data_dict.append({'Name': master_value[0],
        #                       'Count': master_value[1],
        #                       'Abstracts': master_value[2]})
        monthly_df = group_values

        group_by_actual_query = f"""select * from
(SELECT 'The Unstoppable' as team_name,count(abstract_count),sum(abstract_count)
FROM indiatools.tbl_event_status tes
where qc_completed_date between current_date - extract(isodow from current_date)::int and current_date
and qc_person in ('Vinoth Kumar','Dharani R','Kaviarasu P','Chithra P')
group by 1 order by 3 desc) as t1
union
select * from
(SELECT 'Flaming Warriors',count(abstract_count),sum(abstract_count)
FROM indiatools.tbl_event_status tes
where qc_completed_date between current_date - extract(isodow from current_date)::int and current_date
and qc_person in ('Shanmugapriya J','Lakshmanakumar M','Saravanakumar K','Sanjith K')
group by 1 order by 3 desc) as t2
union
select * from
(SELECT 'Fantastic Four' as team_name,count(abstract_count),sum(abstract_count)
FROM indiatools.tbl_event_status tes
where qc_completed_date between current_date - extract(isodow from current_date)::int and current_date
and qc_person in ('Sowbarnika K J','Anisha V','Nivetha S','Karthikeyan M')
group by 1 order by 3 desc) as t3 order by 3 desc"""
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        # data_dict = []
        # for n, master_value in enumerate(group_values, start=1):
        #     data_dict.append({'Team': master_value[0],
        #                       'Count': master_value[1],
        #                       'Abstracts': master_value[2]})
        team_df = group_values

        group_by_actual_query = f"""select qc_person,count(qc_person)  ,sum(abstract_count)  from indiatools.tbl_event_status tes where qc_completed_date  between
                                current_date - extract(isodow from current_date)::int and current_date group by 1 order by 3 desc """
        self.cur.execute(group_by_actual_query)
        group_values = self.cur.fetchall()
        # data_dict = []
        # for n, master_value in enumerate(group_values, start=1):
        #     data_dict.append({'Name': master_value[0],
        #                       'Count': master_value[1],
        #                       'Abstracts': master_value[2]})
        week_individual_df = group_values

        self.con.close()
        return week_individual_df, team_df, monthly_df

    # def test(self):
