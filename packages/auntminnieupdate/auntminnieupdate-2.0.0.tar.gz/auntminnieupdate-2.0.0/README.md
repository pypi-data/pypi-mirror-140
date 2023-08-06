# auntminnnie-update
this package for retirve auntminnie recent news, webinars and radiology conference

# how it work?
his package will scarape in [auntminnnie](https://www.auntminnie.com/) to get latest news, webinars and radiology conference.
and then produce output of excel & csv file or JSON thats ready to use in your web or mobile apps.

there are three features in this package:
- News()
- Conferences()
- webinar()

in some of these function there are serveral function:
- .info() for info how to use
- .test() for testing connection the web
- .singlepage() for scrap data with spesific page. result json, excel & csv file in resultfile. deafult is scrap page 1
- .allpage() for scrap data as many pages availabel. result json, excel & csv file per page & all page in file resultfile
- all in file resultfile with file name according to the features used
- Conferences() only has .singlepage()

i.e auntminnieupdate.News(2) for access page two in news.

# other package that need to be instaled
- BeautifulSoup4
- requests
- pandas(openpyxl)
