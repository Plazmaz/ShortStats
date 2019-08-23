# ShortStats
### Extracting details from shortened bitlinks
This tool is designed for generating aggregate metrics from a list of bitly links using their [link metrics](https://dev.bitly.com/link_metrics.html) API.
You can get an idea of what this might look like by appending a "+" to any bitlink. 
For instance, take the shortened link, [https://bitly.com/1OLp5tz3](https://bitly.com/1OLp5tz3). 
You can view statistics for that link by visiting [https://bitly.com/1OLp5tz3+](https://bitly.com/1OLp5tz3+). ShortStats takes this 
process and automates it. Given a list of bitly links, either through bitly.com or a custom domain, ShortStats will generate metrics across them all.

## Usage
**Note**: You will need a general access token for the examples below (https://bitly.is/accesstoken)  
Some examples:

`python short_stats.py --token <bitly-token> ----save-format json`  

Resume a previous session:  
`python short_stats.py --token <bitly-token> ----save-format json --resume-file outfile.json`

 ```
Usage: short_stats.py [OPTIONS]

Options:
  --in-file FILENAME              The file to pull bitlinks from  [default:
                                  links.txt]
  --token TEXT                    Your bitly generic access token
                                  (https://bitly.is/accesstoken). Can also be
                                  set in BITLY_TOKEN.  [required]
  --quiet                         Skip generating and printing of statistics,
                                  only save data
  --save-format [csv|json]        Specify the output file format.  [default:
                                  json]
  --country-limit-checkpoint INTEGER
                                  The maximum number of countries to display
                                  when reporting progress  [default: 10]
  --country-limit INTEGER         The maximum number of countries to display
                                  when progress is complete.  [default: 30]
  --referrer-limit-checkpoint INTEGER
                                  The maximum number of referrers to display
                                  when reporting progress  [default: 10]
  --referrer-limit INTEGER        The maximum number of referrers to display
                                  when progress is complete.  [default: 30]
  --out-file PATH                 The output filename (extension will be
                                  appended depending on output)  [default:
                                  output]
  --resume-file PATH              The save file to load from. If specified, we
                                  will attempt to resume a previous session
  --start-offset INTEGER          The offset index to start at  [default: 0]
  --help                          Show this message and exit.
```
## Generating/cleaning lists
For an interesting source of bitly links, I suggest using twint (https://github.com/twintproject/twint) for scraping twitter.   
For example, you could use this command to grab bitlinks from tweets posted near the whitehouse:  
`twint -g="32.22682,-95.2255,1km" -s bit.ly`  

You will need to do some cleanup. The group in this regex should match the important part of bit.ly urls:   
`.*https?\://bit\.ly/(.*?)[^\w-].*`  
With this regex, `https://bitly.com/1OLp5tz3` will return `1OLp5tz3`. 
This can then be appended to `bitly.com` to generate a valid link:  
 `bitly.com/1OLp5tz3`.