import cx_Oracle
from pymongo import MongoClient
import pandas as pd
from ukupacha.Utils import Utils
from ukupacha.Utils import is_dict, is_list, is_serie, section_exist, table_exists, parse_table, JsonEncoder
from joblib import Parallel, delayed
import psutil
import json


class UkuPachaGraph:
    def __init__(self, user="system", password="colavudea", dburi="localhost:1521"):
        self.utils = Utils(user=user, password=password, dburi=dburi)

    def request_graph(self, data_row, tables, main_table=None, debug=False):
        if debug:
            print("="*30)
        if not data_row.empty:
            ndata = []
            if main_table is None:
                ndata.append(data_row)
            else:
                ndata.append({"table": main_table, "data": [data_row]})

            for table_dict in tables:
                table = list(table_dict.keys())[0]
                if debug:
                    print(f"table = {table}")
                    print(list(table_dict.keys()))
                if table_dict[table] is not None:
                    for table_relations in table_dict[table]:
                        db = table_relations["DB"]
                        keys = {}
                        for key in table_relations["KEYS"]:
                            alias = key
                            if '/' in key:
                                tmp_keys = key.split('/')
                                key = tmp_keys[0]
                                alias = tmp_keys[1]
                            try:
                                value = data_row[key]
                                if value is not None:
                                    keys[alias] = value
                                else:
                                    if debug:
                                        print(f"None value for key = {key}")
                                        print(data_row)
                                    keys = None
                            except:
                                if debug:
                                    print("-"*30)
                                    print(f"key = {key}")
                                    print(data_row)
                                keys = None
                                continue
                        # con malas llaves no se ppuede hacer el request
                        # y no se puede continuar en profundidad
                        if keys == None:
                            if debug:
                                print("/"*30)
                            continue
                        sub_tables_dict = table_relations["TABLES"]
                        if debug:
                            print(f"len subtables = {len(sub_tables_dict)}")
                        for sub_table_dict in sub_tables_dict:
                            sub_table = list(sub_table_dict.keys())[0]
                            if debug:
                                print(f"sub_table = {sub_table}")

                            try:
                                sub_table_data = []
                                tmp_data = self.utils.request_register(
                                    db, keys, sub_table)
                                for i, row in tmp_data.iterrows():
                                    req_data = self.request_graph(
                                        row, [sub_table_dict], None, debug)
                                    # sub_table_data.append({"table":sub_table,"data":req_data})
                                    sub_table_data.append(req_data)
                                ndata.append(
                                    {"table": sub_table, "data": sub_table_data, "keys": keys})

                            except:
                                if debug:
                                    print(data_row)
                                    print(
                                        f"db = {db} keys={keys} sub_table={sub_table}")
                                    print("|"*30)
                                continue
                else:
                    if debug:
                        print("*"*30)

            return ndata

    def graph2json(self, fields, regs, remove_nulls=True):
        output = {}
        if is_dict(regs):
            table = regs["table"]
            data = regs["data"]
            for i in data:
                value = {}
                if is_serie(i):
                    if table_exists(fields, table):
                        # this allows to jump relatioship tables that are not wanted
                        value = parse_table(fields, table, i, remove_nulls)
                        output.update(value)
                if is_list(i):
                    last_dict = {}
                    for j in i:
                        if is_serie(j):
                            value = parse_table(fields, table, j, remove_nulls)

                        if is_dict(j):
                            last_dict = j
                            out = self.graph2json(fields, j)
                            value.update(out)
                    if table_exists(fields, table):
                        section = fields[table]["alias"]
                        if section == "":
                            output.update(value)
                        else:
                            if section_exist(section, output.keys()):
                                output[section].append(value)
                            else:
                                output[section] = [value]
                    else:
                        if last_dict:
                            sub_table = last_dict["table"]
                            if table_exists(fields, sub_table):
                                section = fields[sub_table]["alias"]
                                if section == "":
                                    output.update(value)
                                else:
                                    if section_exist(section, output.keys()):
                                        if value:  # value !={}
                                            output[section].append(
                                                value[section][0])
                                    else:
                                        if value:
                                            output[section] = [value[section][0]]
                            else:
                                if section_exist("unkown", output.keys()):
                                    output["unkown"].append(value)
                                else:
                                    output["unkown"] = [value]
        else:
            for reg in regs:
                out = self.graph2json(fields, reg)
                output.update(out)
        return output

    def parse_subsections(self, regs, graph_fields):
        sub_section = {}
        for i in graph_fields.keys():
            alias = graph_fields[i]["alias"]
            if "sub_section" in graph_fields[i].keys():
                sub_section[alias] = graph_fields[i]["sub_section"]

        for i in range(len(regs)):
            old_reg = regs[i]
            new_reg = {}
            for j in old_reg.keys():
                if j in sub_section.keys():
                    if sub_section[j] in new_reg.keys():
                        new_reg[sub_section[j]].append({j: old_reg[j]})
                    else:
                        new_reg[sub_section[j]] = [{j: old_reg[j]}]
                else:
                    new_reg[j] = old_reg[j]
            regs[i] = new_reg
        return regs

    def parse_subsection(self, reg, sub_sections):
        new_reg = {}
        for j in reg.keys():
            if j in sub_sections.keys():
                if sub_sections[j] in new_reg.keys():
                    new_reg[sub_sections[j]].append({j: reg[j]})
                else:
                    new_reg[sub_sections[j]] = [{j: reg[j]}]
            else:
                new_reg[j] = reg[j]
        return new_reg

    def run_graph(self, data, graph_schema, max_threads=None, debug=False):
        if max_threads is None:
            jobs = psutil.cpu_count()
        else:
            jobs = max_threads
        regs = Parallel(n_jobs=jobs, backend='threading', verbose=10)(delayed(self.request_graph)(
            row, graph_schema["GRAPH"], main_table=graph_schema["MAIN_TABLE"], debug=0) for i, row in data.iterrows())
        return regs

    def run_graph2json(self, regs, graph_fields):
        output = []
        for reg in regs:
            out = self.graph2json(graph_fields, reg)
            output.append(out)
        return output

    def request_graph2mongodb(self, dbclient, db_name, data_row, tables, main_table, graph_fields, sub_sections):
        try:
            reg = self.request_graph(data_row, tables, main_table)
            raw = self.graph2json(graph_fields, reg)
            out = self.parse_subsection(raw, sub_sections)
            dbclient[db_name][graph_fields[main_table]
                              ["alias"]].insert_one(out)
        except:
            failed_collection = graph_fields[main_table]["alias"]+"_failed"
            print(
                f"Error parsing register, record added to the collection = {failed_collection} ")
            dbclient[db_name][failed_collection].insert_one(data_row.to_dict())

    def run2mongodb(self, data, graph_schema, graph_fields, db_name, mongodb_uri="mongodb://localhost:27017/", max_threads=None):
        sub_sections = {}
        for i in graph_fields.keys():
            alias = graph_fields[i]["alias"]
            if "sub_section" in graph_fields[i].keys():
                sub_sections[alias] = graph_fields[i]["sub_section"]
        dbclient = MongoClient(mongodb_uri)

        if max_threads is None:
            jobs = psutil.cpu_count()
        else:
            jobs = max_threads
        Parallel(n_jobs=jobs, backend='threading', verbose=10)(delayed(self.request_graph2mongodb)(
            dbclient, db_name, row, graph_schema["GRAPH"], graph_schema["MAIN_TABLE"], graph_fields, sub_sections) for i, row in data.iterrows())

    def save_json(self, output_file, data):
        with open(output_file, 'w') as fp:
            json.dump(data, fp, cls=JsonEncoder, indent=4)

    def run2file(self, output_file, data, graph_schema, graph_fields, max_threads=None, debug=False, save_regs=False, save_raws=False):
        regs = self.run_graph(data, graph_schema, max_threads, debug)
        if save_regs:
            self.save_json(output_file+".regs.json", regs)

        raws = self.run_graph2json(regs, graph_fields)
        if save_raws:
            self.save_json(output_file+".raws.json", raws)

        output = self.parse_subsections(raws, graph_fields)
        self.save_json(output_file, output)
        print(f"Process finished, file {output_file} save")
