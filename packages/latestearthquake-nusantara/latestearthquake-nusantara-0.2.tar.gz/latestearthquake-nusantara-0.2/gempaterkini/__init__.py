import requests
from bs4 import BeautifulSoup


def ekstraksi_data():
    """
    Tanggal: 15 Februari 2022
    Waktu: 16:51:43 WIB
    Magnitudo: 3.4
    Kedalaman: 10 km
    Koordinat: LS=0.72 LS  BT=131.51 BT
    Lokasi: Pusat gempa berada di laut 29 km Timur Laut Kota Sorong
    Dirasakan: (Skala MMI): II Kota Sorong
    :return:
    """

    try:
        content = requests.get('https://bmkg.go.id')
    except Exception:
        return None
    if content.status_code == 200:
        soup = BeautifulSoup(content.text, 'html.parser')

        kapan = soup.find('span', {'class': 'waktu'})
        kapan = kapan.text.split(', ')
        tanggal = kapan[0]
        waktu = kapan[1]


        kapan = soup.find('div', {'class': 'col-md-6 col-xs-6 gempabumi-detail no-padding'})
        kapan = kapan.findChildren('li')
        i = 0
        magnitudo = None
        kedalaman = None
        ls = None
        bt = None
        lokasi = None
        dirasakan = None

        for res in kapan:
            if i == 1:
                magnitudo = res.text
            elif i == 2:
                kedalaman = res.text
            elif i == 3:
                koordinat = res.text.split(' - ')
                ls = koordinat[0]
                bt = koordinat[1]
            elif i == 4:
                lokasi = res.text
            elif i == 5:
                dirasakan = res.text
            i = i + 1

        hasil = dict()
        hasil['tanggal'] = tanggal
        hasil['waktu'] = waktu
        hasil['magnitudo'] = magnitudo
        hasil['kedalaman'] = kedalaman
        hasil['koordinat'] = {'ls':ls,   'bt':bt }
        hasil['lokasi'] = lokasi
        hasil['dirasakan'] = dirasakan
        return hasil
    else:
        return None



def tampilkan_data(result):
    if result is None:
        print("Tidak bisa menemukan data gempa terkini")
        return

    print('Gempa Terakhir berdasarkan BMKG')
    print(f"Tanggal: {result['tanggal']}")
    print(f"Waktu: {result['waktu']}")
    print(f"Magnitudo: {result['magnitudo']}")
    print(f"Kedalaman: {result['kedalaman']}")
    print(f"Koordinat: LS={result['koordinat']['ls']}, BT={result['koordinat']['bt']}")
    print(f"Lokasi: {result['lokasi']}")
    print(f"Dirasakan: {result['dirasakan']}")


if __name__ == '__main__':
    result = ekstraksi_data()
    tampilkan_data(result)