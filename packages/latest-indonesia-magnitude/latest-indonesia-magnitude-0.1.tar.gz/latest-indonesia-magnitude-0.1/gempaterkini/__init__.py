import requests
from bs4 import BeautifulSoup

def ekstraksi_data():
    try:
        content = requests.get('https://bmkg.go.id')
    except Exception:
        print('alamat salah')
        return None

    if content.status_code == 200:
        soup = BeautifulSoup(content.text, 'html.parser')
        result = soup.find('span', {'class': 'waktu'})
        result = result.text.split(', ')
        tanggal = result[0]
        waktu = result[1]

        result = soup.find('div', {'class': 'col-md-6 col-xs-6 gempabumi-detail no-padding'})
        result = result.findChildren('li')
        i = 0
        for res in result:
            if i == 1:
                magnitude = res.text
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
        hasil['magnitude'] = magnitude
        hasil['kedalaman'] = kedalaman
        hasil['koordinat'] = {'ls':ls, 'bt':bt}
        hasil['lokasi'] = lokasi
        hasil['dirasakan'] = dirasakan
        return hasil
    else:
        print('alamat web salah')
        return None

def tampilkan_data(result):
    if result is None:
        print("tidak bisa menemukan  data terkini")
        return
    print('Gempa terkini berdasarkan BMKG')
    print(f"Tanggal {result['tanggal']}")
    print(f"Waktu  {result['waktu']}")
    print(f"Magnitudo  {result['magnitude']}")
    print(f"Kedalaman  {result['kedalaman']}")
    print(f"Lokasi  {result['lokasi']}")
    print(f"Koordinat: Lintang={result['koordinat']['ls']}, Bujur={result['koordinat']['bt']}")
    print(f"Dirasakan  {result['dirasakan']}")
    print('\n==============')
    print("Tanggal", result['tanggal'])
    print("Waktu", {result['waktu']})
    result = ekstraksi_data()
    print(result)
#    pass
if __name__ == '__main__':
    result = ekstraksi_data()
    tampilkan_data(result)

