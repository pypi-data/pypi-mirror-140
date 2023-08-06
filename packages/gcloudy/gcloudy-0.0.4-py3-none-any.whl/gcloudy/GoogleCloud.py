from google.cloud import bigquery

class BigQuery():
    
    def __init__(self, project_id):
        self.project_id = project_id
        
    def __repr__(self):
        return(f"|-----|  BigQuery connector instance  |-----|\n -- current Project ID: {self.project_id}")
    
    
    def read_bigquery(self, bq_dataset_dot_table = None, preview_top = None, to_verbose = True):
        if bq_dataset_dot_table is None:
            print("please provide a 'dataset_id.table_name' arg to 'bq_dataset_dot_table'")
            return None
        if len(bq_dataset_dot_table.split(".")) < 2:
            print("the string passed to 'bq_dataset_dot_table' must have both a 'dataset_id' and 'table_name' seperated by a dot")
            print("example: 'my_dataset.my_table_name'")
            return None
        bq_path = ".".join([self.project_id, bq_dataset_dot_table])
        if preview_top is None:
            if to_verbose:
                print(f"-- querying all rows from {bq_path}")
            que = f"SELECT * FROM `{bq_path}`"
        else:
            if to_verbose:
                print(f"-- querying only top {preview_top} rows from {bq_path}")
            que = f"SELECT * FROM `{bq_path}` LIMIT {preview_top}"
        client = bigquery.Client()
        ret = client.query(que).to_dataframe()
        if to_verbose:
            print(f"-- returned {ret.shape[0]} rows and {ret.shape[1]} columns")
        return ret
    
    
    def write_bigquery(self, df, bq_dataset_dot_table = None, use_schema = None, append_to_existing = False, to_verbose = True):
        if bq_dataset_dot_table is None:
            print("please provide a 'dataset_id.table_name' arg to 'bq_dataset_dot_table'")
            return None
        if len(bq_dataset_dot_table.split(".")) < 2:
            print("the string passed to 'bq_dataset_dot_table' must have both a 'dataset_id' and 'table_name' seperated by a dot")
            print("example: 'my_dataset.my_table_name'")
            return None
        bq_path = ".".join([self.project_id, bq_dataset_dot_table])
        if append_to_existing:
            if to_verbose:
                print(f"-- appending to existing table {bq_dataset_dot_table}")
            if use_schema is None:
                if to_verbose:
                    print("-- using auto-detected schema")
                job_config = bigquery.LoadJobConfig(
                    autodetect = True,
                    write_disposition = bigquery.WriteDisposition.WRITE_APPEND
                )
            else:
                if to_verbose:
                    print("-- using custom user-provided schema")
                job_config = bigquery.LoadJobConfig(
                    autodetect = False,
                    schema = use_schema,
                    write_disposition = bigquery.WriteDisposition.WRITE_APPEND
                )
        else:
            if to_verbose:
                print(f"-- creating a new table {bq_dataset_dot_table} (or overwriting if already exists)")
            if use_schema is None:
                if to_verbose:
                    print("-- using auto-detected schema")
                job_config = bigquery.LoadJobConfig(
                    autodetect = True,
                    write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
                )
            else:
                if to_verbose:
                    print("-- using custom user-provided schema")
                job_config = bigquery.LoadJobConfig(
                    autodetect = False,
                    schema = use_schema,
                    write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
                )
        client = bigquery.Client()
        load_job = client.load_table_from_dataframe(df, bq_path, job_config = job_config)
        load_job.result()
        ret = client.get_table(bq_path)
        if to_verbose:
            print(f"-- {ret.num_rows} rows have been successfully written to {bq_path}")
            
            
    def read_custom_query(self, custom_query, to_verbose = True):
        client = bigquery.Client()
        ret = client.query(custom_query).to_dataframe()
        if to_verbose:
            print(f"-- returned {ret.shape[0]} rows and {ret.shape[1]} columns")
        return ret


    def send_query(self, que, to_verbose = True):
        if to_verbose:
            print("-- sending query ...")
        client = bigquery.Client()
        qconf = bigquery.QueryJobConfig()
        qjob = client.query(que, job_config = qconf)
        qjob.result()
        if to_verbose:
            print("-- query complete")
