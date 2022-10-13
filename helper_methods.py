from cmath import inf
import os
import csv
import requests
from requests.adapters import HTTPAdapter, Retry

import json

from soupsieve import escape

class party_result:
    def __init__(self, name, total_votes, direct_mandates, compensation_mandates) -> None:
        self.name = name
        self.total_votes = total_votes
        self.direct_mandates = direct_mandates
        self.compensation_mandates = compensation_mandates

class folder_structure:
    def __init__(self, path):
        self.root_folder = path
        self.psBiH = path + "/PSBiH"
        
        self.presidency = path + "/presidency"
        self.bosniakPresidency = self.presidency + "/Bosniak"
        self.croatPresidency = self.presidency + "/Croat"
        self.serbPresidency = self.presidency + "/Serb"

        self.pFBiH = path + "/PFBiH"
        self.nsrs = path + "/nsrs"
        self.kantons = path + "/kantons"

        self.predRS = path + "/predRS"

    def create_root_folder(self):
        os.mkdir(self.root_folder)

    def create_psbih_folder(self):
        os.mkdir(self.psBiH)
    
    def create_presidency_root_folder(self):
        os.mkdir(self.presidency)
    
    def create_bosniak_presidency_folder(self):
        os.mkdir(self.bosniakPresidency)
    
    def create_croat_presidency_folder(self):
        os.mkdir(self.croatPresidency)
    
    def create_serb_presidency_folder(self):
        os.mkdir(self.serbPresidency)
    
    def create_all_presidency_folders(self):
        self.create_presidency_root_folder()
        self.create_bosniak_presidency_folder()
        self.create_croat_presidency_folder()
        self.create_serb_presidency_folder()

    def create_pfbih_folder(self):
        os.mkdir(self.pFBiH)
    
    def create_nsrs_folder(self):
        os.mkdir(self.nsrs)

    def create_predrs_folder(self):
        os.mkdir(self.predRS)

    def create_kanton_folder(self):
        os.mkdir(self.kantons)
    
    def generate_folders(self):
        self.create_root_folder()
        self.create_all_presidency_folders()
        self.create_psbih_folder()
        self.create_pfbih_folder()
        self.create_nsrs_folder()
        self.create_kanton_folder()
        self.create_predrs_folder()

class election:
    def __init__(self, election_name) -> None:
        self.name = election_name
def generate_folder_structure(currentTime):
    folders = folder_structure("rezultati_"+currentTime)
    folders.generate_folders()
    return folders

def get_and_save_data(link, filepath):
    data = get_data_from_izbori(link).json()
    
    with open(filepath+".json", "w") as outfile:
        json.dump(data, outfile)
    
    write_csv_from_json(filepath, data)
    return data

def get_basic_info(election_name, election_code, filepath):
    link_stub = f"https://www.izbori.ba/api_2018/{election_code}/{election_name}" 
    return get_and_save_data(link_stub, filepath)

def get_results_from_race(election_name, race_name, race_code,filepath):
    race_stub = f"https://www.izbori.ba/api_2018/{race_name}/{election_name}/{race_code}/1"
    return get_and_save_data(race_stub, filepath)

def get_entity_party_result(election_name, race_name):
    if race_name == "race6":
        race_stub = f"https://www.izbori.ba/api_2018/{race_name}_basicinfopartyresult/{election_name}/1"    
    else:
        race_stub = f"https://www.izbori.ba/api_2018/{race_name}_entitypartyresult/{election_name}/1"
    return get_data_from_izbori(race_stub)

def get_presidency_results_overall(election_name, folders):
        
    get_basic_info(election_name, "race1_basicinfo",folders.presidency+"/overallData.csv")
    get_results_from_race(election_name, "race1_memberpresidencycandidatesresult",701, folders.bosniakPresidency+"/results.csv")
    get_results_from_race(election_name, "race1_memberpresidencycandidatesresult",702, folders.croatPresidency+"/results.csv")
    get_results_from_race(election_name, "race1_memberpresidencycandidatesresult",703, folders.serbPresidency+"/results.csv")
    
def get_rs_presidency_result_overall(election_name, folders):
    predrs_link = f"https://www.izbori.ba/race5_candidatesresult/{election_name/1}"
    get_and_save_data(predrs_link,folders)

def get_presidency_results_municipal(election_name, presidency_root):
    opcine_fbih_link = "https://www.izbori.ba/api_2018/race1_electoralunit/%22WebResult_2018GEN_2018_10_4_15_40_5%22/1/1"
    opcine_rs_link = "https://www.izbori.ba/api_2018/race1_electoralunit/%22WebResult_2018GEN_2018_10_4_15_40_5%22/1/2"

    with open("fbih_municipalities.json", "r") as infile:
        fbih_municipalities = json.load(infile)

    with open("rs_municipalities.json", "r") as infile:
        rs_municipalities = json.load(infile)

    basic_info_stub = f"https://www.izbori.ba/api_2018/race1_electoralunitbasicinfo/{election_name}/6"
    results_stub = f"https://www.izbori.ba/api_2018/race1_electoralunitcandidatesresult/{election_name}/6/1"

    all_results = []
    all_data = []
    for op in fbih_municipalities:
        basic_opcina_data_link = f"https://www.izbori.ba/api_2018/race1_electoralunitbasicinfo/{election_name}/{op['code']}"
        basic_opcina_result_link = f"https://www.izbori.ba/api_2018/race1_electoralunitcandidatesresult/{election_name}/{op['code']}/1"

        #basic_opcina_data = requests.get(basic_opcina_data_link).json()
        basic_opcina_data = get_data_from_izbori(basic_opcina_data_link).json()
        basic_opcina_data['municipality'] = op['name']
        basic_opcina_data['municipality_code'] = op['code']
        basic_opcina_data['entity'] = 'fbih'
        all_data.append(basic_opcina_data)

        basic_opcina_results = get_data_from_izbori(basic_opcina_result_link).json()
        for res in basic_opcina_results:
            res['municipality'] = op['name']
            res['municipality_code'] = op['code']
            res['entity'] = 'fbih'
        all_results.append(basic_opcina_results)
    
    for op in rs_municipalities:
        basic_opcina_data_link = f"https://www.izbori.ba/api_2018/race1_electoralunitbasicinfo/{election_name}/{op['code']}"
        basic_opcina_result_link = f"https://www.izbori.ba/api_2018/race1_electoralunitcandidatesresult/{election_name}/{op['code']}/1"
        
        basic_opcina_data = requests.get(basic_opcina_data_link).json()
        basic_opcina_data['municipality'] = op['name']
        basic_opcina_data['municipality_code'] = op['code']
        basic_opcina_data['entity'] = "RS"
        all_data.append(basic_opcina_data)

        basic_opcina_results = requests.get(basic_opcina_result_link).json()
        for res in basic_opcina_results:
            res['municipality'] = op['name']
            res['municipality_code'] = op['code']
            res['entity'] = "RS"

        all_results.append(basic_opcina_results)

    all_results = flatten(all_results)
    write_csv_from_json(presidency_root + "/municipal_results.csv", all_results)
    write_csv_from_json(presidency_root + "/municipal_data.csv", all_data)

def write_csv_from_json(filepath, datadict):

    if type(datadict) is dict:
        write_oneline_csv_from_json(filepath, datadict)
    if type(datadict) is list:
        write_multiline_csv_from_json(filepath, datadict)

def write_oneline_csv_from_json(filepath, datadict):
    keys = datadict.keys()
    with open(filepath, "w") as outfile:
        dict_writer = csv.DictWriter(outfile, keys)
        dict_writer.writeheader()
        dict_writer.writerow(datadict)

def write_multiline_csv_from_json(filepath, datadict):
    keys = datadict[0].keys()
    with open(filepath, "w") as outfile:
        dict_writer = csv.DictWriter(outfile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(datadict)

def flatten(l):
    return [item for sublist in l for item in sublist]

def flatten_mandates_results(party_results_per_unit):
    flattened_data = []
    for unit in party_results_per_unit:
        for party in party_results_per_unit[unit]:
            flattened_data.append({
                "unit": unit,
                "party": party,
                "mandates": party_results_per_unit[unit][party]['mandates']
            })
    return flattened_data

def get_unit_results(election_name, race_name):
    if race_name == "race4" or race_name == "race2" or race_name == "race6":
        unit_list_link = f"https://www.izbori.ba/api_2018/{race_name}_electoralunitparent/{election_name}/0/1"
    else:
        unit_list_link = f"https://www.izbori.ba/api_2018/{race_name}_electoralunitparent/{election_name}/1"
    list_of_units = get_data_from_izbori(unit_list_link).json()

    all_unit_results = {}
    for unit in list_of_units:
        link_unit_party_results = f"https://www.izbori.ba/api_2018/{race_name}_electoralunitparentpartyresult/{election_name}/{unit['code']}/1"
        unit_results = get_data_from_izbori(link_unit_party_results).json()
        
        for result in unit_results:
            result['unit_code'] = unit['code']
            result['unit_name'] = unit['name']
            all_unit_results[unit['code']] = unit_results
    
    return all_unit_results

def get_kanton_results_overall(election_name,path):
    kanton_results = get_unit_results(election_name, "race7")
    seats_per_kanton = {"201": 30,"202": 21,"203": 35,"204": 35,"205": 25,"206": 30,"207": 30,"208": 23,"209": 35,"210": 25}
    all_kanton_mandates = {}
    for kanton in seats_per_kanton:
        mandates = calculate_mandates(kanton_results[kanton],0.03,seats_per_kanton[kanton])
        all_kanton_mandates[kanton] = mandates

    flatened_mandates = flatten_mandates_results(all_kanton_mandates)
    write_csv_from_json(path+"/rezultati.csv", flatten_kanton_results(kanton_results))
    write_csv_from_json(path+"/mandates.csv", flatened_mandates)
    with open(path+"/rezultati.json","w") as outfile:
        json.dump(kanton_results, outfile)

    print(flatened_mandates)
    return kanton_results

def flatten_kanton_results(results):
    results_list=[]
    for unit in results:
        for result in results[unit]:
            results_list.append(result)
    return results_list

def get_nsrs_results_overall(election_name, path):
    link_nsrs_units_link = f"https://www.izbori.ba/api_2018/race6_electoralunitparent/{election_name}/0/1"
    nsrs_units = get_data_from_izbori(link_nsrs_units_link)

    link_nsrs_overall = f"https://www.izbori.ba/api_2018/race6_basicinfopartyresult/{election_name}/1"
    nsrs_overall = get_data_from_izbori(link_nsrs_overall).json()
    write_csv_from_json(path+"/rezultati_overall.csv", nsrs_overall)

    all_nsrs_results = []
    for unit in nsrs_units:
        link_nsrs_parties = f"https://www.izbori.ba/api_2018/race6_electoralunitparentpartyresult/{election_name}/{unit['code']}/1"
        nsrs_result = get_data_from_izbori(link_nsrs_parties).json()


def get_pred_rs_overall(election_name, path):
    link_pred_rs_overall = f"https://www.izbori.ba/api_2018/race5_candidatesresult/{election_name}/1"
    pred_rs_overall = get_data_from_izbori(link_pred_rs_overall).json()
    print(pred_rs_overall)
    write_csv_from_json(path+"/rezultati.csv", pred_rs_overall)

def get_ps_bih_results(election_name, path):

    link_ps_bih_overall_fbih = f"https://www.izbori.ba/api_2018/race2_entitypartyresult/{election_name}/1/1"
    link_ps_bih_overall_rs = f"https://www.izbori.ba/api_2018/race2_entitypartyresult/{election_name}/2/1"

    overall_results_fbih = get_data_from_izbori(link_ps_bih_overall_fbih).json()
    overall_results_rs = get_data_from_izbori(link_ps_bih_overall_rs).json()

    write_csv_from_json(path+"/fbih.csv", overall_results_fbih)
    write_csv_from_json(path+"/rs.csv", overall_results_rs)

    unit_results = get_unit_results(election_name,"race2")
    fbih_mandates_direct = {"511":3,"512":3,"513":4,"514":6,"515":5 }
    rs_mandates_direct = {"521":3,"522":3,"523":3}


    rs_unit_results = {unit:unit_results[unit] for unit in unit_results if unit in rs_mandates_direct}
    fbih_unit_results = {unit:unit_results[unit] for unit in unit_results if unit in fbih_mandates_direct}
    print(rs_unit_results)
    with open("psbih_units.json","w") as outfile:
        json.dump(unit_results, outfile)
    with open("psbih_rs_results.json","w") as outfile:
        json.dump(overall_results_rs, outfile)
    with open("psbih_fbih_results.json","w") as outfile:
        json.dump(overall_results_fbih, outfile)
    
    rs_mandates = calculate_direct_and_compensation_mandates(rs_unit_results, overall_results_rs, 0.03, rs_mandates_direct,5)
    write_csv_from_json(path+"/rs_mandates.csv", rs_mandates)
    fbih_mandates = calculate_direct_and_compensation_mandates(fbih_unit_results, overall_results_fbih, 0.03, fbih_mandates_direct,7)
    write_csv_from_json(path+"/fbih_mandates.csv", fbih_mandates)
    

def get_parlfbih_results(election_name, path):
    reps_per_unit = {"401":9,"402":5,"403":7, "404": 4, "405": 8, "406":4, "407":6, "408":9, "409":8, "410": 3, "411":7, "412": 3}

    return get_entity_level_results(election_name, "race4", reps_per_unit, 25,0.03, path)
    
def get_entity_level_results(election_name, race_name, reps_per_unit, compensation_mandates, threshold, path):
    entity_unit_results = get_unit_results(election_name, race_name)
    all_level_mandates = {}

    for unit in reps_per_unit:
        mandates = calculate_mandates(entity_unit_results[unit], threshold, reps_per_unit[unit])
        all_level_mandates[unit] = mandates

    flatened_mandates = flatten_mandates_results(all_level_mandates)
    mandates_per_party = {}
    for mandate in flatened_mandates:
        if mandate['party'] in mandates_per_party:
            mandates_per_party[mandate['party']] += mandate['mandates']
        else:
            mandates_per_party[mandate['party']] = mandate['mandates']
    
    entity_overall_party_results = get_entity_party_result(election_name, race_name).json()
    compensation_mandates = calculate_mandates_with_compensation(entity_overall_party_results,threshold,compensation_mandates,mandates_per_party)

    printeable_mandates = []
    for mandate in mandates_per_party:
        if mandate in compensation_mandates:
            printeable_mandates.append({"party": mandate, "mandates":mandates_per_party[mandate], 
            "compensation": compensation_mandates[mandate]['compensation'], "total": mandates_per_party[mandate] + compensation_mandates[mandate]['compensation']})
        else:
            printeable_mandates.append({"party": mandate, "mandates":mandates_per_party[mandate], 
            "compensation": 0, "total": mandates_per_party[mandate]})
    
    for mandate in compensation_mandates:
        if mandate not in mandates_per_party:
            printeable_mandates.append({"party": mandate, "mandates":0, 
            "compensation": compensation_mandates[mandate]['compensation'], "total": compensation_mandates[mandate]['compensation']})
    

    write_csv_from_json(path+"/rezultati.csv", flatten_kanton_results(entity_unit_results))
    write_csv_from_json(path+"/mandates.csv", printeable_mandates)
    with open(path+"/rezultati.json","w") as outfile:
        json.dump(entity_unit_results, outfile)

    print(flatened_mandates)
    return entity_unit_results

def get_nsrs_results(election_name, path):
    reps_per_unit = {
        "301":7,
        "302":7,
        "303":12,
        "304":4,
        "305":6,
        "306":9,
        "307":4,
        "309":7
    }
    return get_entity_level_results(election_name, "race6", reps_per_unit,20,0.03, path)
def get_data_from_izbori(uri):

    s = requests.Session()

    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ])

    s.mount('https://', HTTPAdapter(max_retries=retries))

    result = s.get(uri)
    return result

def calculate_direct_and_compensation_mandates(party_results, overall_results, threshold, direct_seats_per_unit, compensation_mandates):
    all_level_mandates = {}

    for unit in direct_seats_per_unit:
        mandates = calculate_mandates(party_results[unit], threshold, direct_seats_per_unit[unit])
        all_level_mandates[unit] = mandates
    
    flattened_mandates = flatten_mandates_results(all_level_mandates)

    mandates_per_party = {}
    for mandate in flattened_mandates:
        if mandate['party'] in mandates_per_party:
            mandates_per_party[mandate['party']] += mandate['mandates']
        else:
            mandates_per_party[mandate['party']] = mandate['mandates']
    
    compensation_mandates = calculate_mandates_with_compensation(overall_results, threshold, compensation_mandates, mandates_per_party)

    printeable_mandates = []
    for mandate in mandates_per_party:
        if mandate in compensation_mandates:
            printeable_mandates.append({"party": mandate, "mandates":mandates_per_party[mandate], 
            "compensation": compensation_mandates[mandate]['compensation'], "total": mandates_per_party[mandate] + compensation_mandates[mandate]['compensation']})
        else:
            printeable_mandates.append({"party": mandate, "mandates":mandates_per_party[mandate], 
            "compensation": 0, "total": mandates_per_party[mandate]})
    
    for mandate in compensation_mandates:
        if mandate not in mandates_per_party:
            printeable_mandates.append({"party": mandate, "mandates":0, 
            "compensation": compensation_mandates[mandate]['compensation'], "total": compensation_mandates[mandate]['compensation']})
    
    return printeable_mandates
def calculate_mandates(party_results, threshold, seats_to_assign):
    
    sum_of_votes = sum(r['totalVotes'] for r in party_results)
    workableResults = [{"totalVotes":x['totalVotes'], "originalVotes":x['totalVotes'], "name":x['name']} for x in party_results if x['totalVotes'] >= sum_of_votes*threshold]
    mandates_per_party = {}
    sorted_list = sorted(workableResults, key=lambda d: d['totalVotes'], reverse=True) 

    for round in range(0,seats_to_assign):
        highest_votes = sorted_list[0]
        if highest_votes['name'] in mandates_per_party:
            mandates_per_party[highest_votes['name']]['mandates'] += 1
            mandates_per_party[highest_votes['name']]['dividor'] += 2
            sorted_list[0]['totalVotes'] = sorted_list[0]['originalVotes'] / (mandates_per_party[highest_votes['name']]['dividor']+2)
        else:
            mandates_per_party[highest_votes['name']] = {"mandates" :1, "dividor":1}
            sorted_list[0]['totalVotes'] = sorted_list[0]['originalVotes'] / (mandates_per_party[highest_votes['name']]['dividor']+2)

        sorted_list = sorted(sorted_list, key=lambda d: d['totalVotes'], reverse=True) 
    return mandates_per_party

def calculate_mandates_with_compensation(party_results, threshold, seats_to_assign, direct_mandates):
    sum_of_votes = sum(r['totalVotes'] for r in party_results)
    workableResults = [{"totalVotes":x['totalVotes'], "originalVotes":x['totalVotes'], "name":x['name']} for x in party_results if x['totalVotes'] >= sum_of_votes*threshold]

    for result in workableResults: #if has direct mandates, divide
        if result['name'] in direct_mandates:
            result['totalVotes'] = result['totalVotes'] / get_odd_number(direct_mandates[result['name']] + 1)
            result['dividor'] = get_odd_number(direct_mandates[result['name']] + 1)
    sorted_list = sorted(workableResults, key=lambda d: d['totalVotes'], reverse=True) 
    compensation_mandates = {}
    
    for round in range(0,seats_to_assign):
        highest_votes = sorted_list[0]
        if highest_votes['name'] in compensation_mandates:
            compensation_mandates[highest_votes['name']]['compensation'] += 1
            compensation_mandates[highest_votes['name']]['dividor'] += 2
            sorted_list[0]['totalVotes'] = sorted_list[0]['originalVotes'] / compensation_mandates[highest_votes['name']]['dividor']
        elif highest_votes['name'] in direct_mandates:
            divider = get_odd_number(direct_mandates[highest_votes['name']]+2)
            compensation_mandates[highest_votes['name']] = {"compensation" :1, "dividor":divider}
            sorted_list[0]['totalVotes'] = sorted_list[0]['originalVotes'] / divider
        else:
            compensation_mandates[highest_votes['name']] = {"compensation" :1, "dividor": 3}
            sorted_list[0]['totalVotes'] = sorted_list[0]['originalVotes'] / 3


        sorted_list = sorted(sorted_list, key=lambda d: d['totalVotes'], reverse=True) 
    return compensation_mandates

def get_odd_number(number):
    num = -1
    for i in range(0,number):
        num+=2
    return num