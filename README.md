# Year sheet
Give me a list of 365 values and I'll hand you a GitHub-style contribution chart out of them.

## Installation
Install the dependencies (just numpy, pandas and bokeh):
```
pip install -r requirements.txt
```

## Call the sample
```
python3 year_sheet.py
```

**Command line args**  
`-s` `--source` a path to a file with 365 or 366 lines full of floats.  
`-y` `--year` Just for giving the chart a compelling name.   
`-b` `--bare` Display only the year sheet. Otherwise it shows also a week load with the aggregated values per week.  

When no arguments are passed it generates 365 random positive values and plots them.  

Notice that when year and data are provided both should match so be aware of leap years.  

## Screenshots
Just open the sheet.html sample in your browser.

