# frontend/app.py
import streamlit as st
import requests
import os

GOOGLE_MAPS_API_KEY=os.getenv("GOOGLE_MAPS_API_KEY")

# 표시할 주소 리스트
addresses = [
    '서울특별시 강남구 테헤란로 123',
    '서울특별시 종로구 세종대로 456',
    # 추가 주소들...
]

# HTML 템플릿
html_template = '''
<!DOCTYPE html>
<html>
  <head>
    <title>Google Maps</title>
    <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&callback=initMap" async defer></script>
    <script>
      function initMap() {{
        var map = new google.maps.Map(document.getElementById('map'), {{
          zoom: 12,
          center: {{lat: 37.5665, lng: 126.9780}}  // 서울 중심 좌표
        }});

        var geocoder = new google.maps.Geocoder();
        var addresses = {addresses};

        addresses.forEach(function(address) {{
          geocoder.geocode({{'address': address}}, function(results, status) {{
            if (status === 'OK') {{
              var marker = new google.maps.Marker({{
                map: map,
                position: results[0].geometry.location,
                title: address
              }});
            }} else {{
              console.error('Geocode was not successful for the following reason: ' + status);
            }}
          }});
        }});
      }}
    </script>
  </head>
  <body>
    <div id="map" style="height: 500px; width: 100%;"></div>
  </body>
</html>
'''

# 주소 리스트를 JavaScript 배열 형식으로 변환
addresses_js = str(addresses).replace("'", '"')

# HTML 코드 생성
html_code = html_template.format(api_key=GOOGLE_MAPS_API_KEY, addresses=addresses_js)


st.title("엑셀파일 업로드하기")

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file is not None:
    response = requests.post("http://localhost:8000/upload/", files={"file": uploaded_file})
    
    if response.status_code == 200:
        data = response.json().get("data", [])
        juso_key = [key for key in data[0].keys() if '주소' in key]
        st.write("추출된 주소 목록:")
        for datum in data:
            st.write(datum.get(juso_key[0]))
        st.components.v1.html(html_code, height=500)
    else:
        st.error("파일 처리에 실패했습니다. 올바른 파일을 업로드하세요.")

