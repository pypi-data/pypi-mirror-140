# DataDictionary

AutoDataDictionary generates data dictionary from source files and database tables including:
  - Column Name
  - Sample Value
  - Source File Name
  - Non Null Values Count
  - Unique Values Count
  - Data Type
  - Unique Values List

### How to use

Generate data dictionary from db
   ```{python}
   import autodatadictionary as ad
   
   ad.to_dictionary_from_db(
        sql_alchemy_connection_string='postgresql://username:password@domain:5432/db',
        schema='schema')
   ```

Generate data dictionary from csv files
   ```{python}
   import autodatadictionary as ad
   
   ad.to_dictionary_from_file(['/path/data1.csv', '/path/data2.csv', '/path/dataN.csv'], sep=',')
   ```

Generate data dictionary from dataframe
   ```{python}
   import autodatadictionary as ad
   
   titanic = pd.read_csv('https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv')
   ad.to_dictionary_from_dataframe([titanic])
   ad.to_dictionary_from_dataframe(dataframes=[titanic], source_names=['titanic_dataframe'], source=True)
   ```