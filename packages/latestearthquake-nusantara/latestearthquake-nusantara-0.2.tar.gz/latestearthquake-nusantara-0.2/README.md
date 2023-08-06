# Latest Indonesia EarthQuake
This package will get the latest earthquake from BMKG | Meteorogical, Climatological, and Geophysical Agency

## HOW IT WORK?
This package will scrape from [BMKG](https://bmkg.go.id) to get latest quake happened in Indonesia.

This package will use BeautifulSoup4 and Requests to pruduce output in the form of JSON that is ready to be used in web or mobile applications

## HOW TO USE
    import gempaterkini

    if __name__ == '__main__':
        result = gempaterkini.ekstraksi_data()
        gempaterkini.tampilkan_data(result)


# Author
Muhammad Ihsan