from dotenv import load_dotenv
import os
import neo4j_db_connector as nc
import pandas as pd


def fill_metamodel(connection, delete_all=True):
    concepts_df = pd.read_csv("metamodel/concepts.csv")
    relations_df = pd.read_csv("metamodel/relations.csv")

    if delete_all:
        connection.query('MATCH (n:Meta) DETACH DELETE n')

    for _, concept_row in concepts_df.iterrows():
        properties_str = ''
        for p_name in concepts_df.columns:
            if p_name != 'labels' and type(concept_row[p_name]) != float:
                # type(concept_row[p_name]) != float - фильтрация пустых значений
                if p_name in ['name', 'description', 'eventName', 'propertyName']:
                    properties_str += f"{p_name}: '{concept_row[p_name]}', "
                if p_name == 'nodeType':
                    properties_str += f"{p_name}: {concept_row[p_name].split(',')}, "
        properties_str = properties_str[:-2]
        query = f"CREATE (:{':'.join(concept_row['labels'].split(','))} {{{properties_str}}})"
        print(query)
        connection.query(query)

    for _, relation_row in relations_df.iterrows():
        query = f"""MATCH (a {{name: '{relation_row['from']}'}}), (b {{name: '{relation_row['to']}'}}) 
        CREATE (a)-[:{relation_row['label']} {{name: '{relation_row['name']}'}}]->(b)"""
        print(query)
        connection.query(query)


if __name__ == '__main__':
    load_dotenv()
    conn = nc.Neo4jConnection(uri=os.getenv("URI"), user=os.getenv("USERNAME"), pwd=os.getenv("PASSWORD"))
    # conn = nc.Neo4jConnection(uri=os.getenv("URI_CLOUD"), user=os.getenv("USERNAME_CLOUD"),
    #                           pwd=os.getenv("PASSWORD_CLOUD"))
    fill_metamodel(conn)






