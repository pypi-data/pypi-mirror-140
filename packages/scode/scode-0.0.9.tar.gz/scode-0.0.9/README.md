# scode
![PyPI](https://img.shields.io/pypi/v/scode)
![PyPI - Downloads](https://img.shields.io/pypi/dm/scode)

## Installaion (설치)

cmd창을 열어서 하단의 코드를 입력 후 실행.

```bash
pip install scode
```

## Example (사용예시)

```py
from scode.selenium import * # scode의 selenium 모듈의 모든 것을 임포트

driver = load_driver()
```

or

```py
from scode.selenium import load_driver # scode의 selenium 모듈의 load_driver만 임포트

driver = load_driver()
```

or

```py
import scode.selenium # scode의 selenium 모듈을 임포트, 이 경우에는 하단처럼 전체 경로를 입력해야 함

driver = scode.selenium.load_driver()
```

or

```py
import scode # 이 경우에는 하단처럼 전체 경로를 입력해야 함

driver = scode.selenium.load_driver()
```

## 구조도 (트리구조)

* scode
	* dropbox
		* dropbox_upload_file(src_file_path, destination_path) : 드롭박스에 파일을 업로드 하는 함수
		* dropbox_upload_folder(folder_path, destination_path) : 드롭박스에 폴더를 업로드 하는 함수
	* paramiko
		* command(ssh: paramiko.SSHClient, query: str, timeout = None) : 서버에 명령어를 실행하는 함수
		* execute_sql_query(ssh: paramiko.SSHClient, user_id: str, user_pw: str, db_name: str, query: str) : 파라미코로 mysql 쿼리를 실행하는 함수
		* ssh_connect(hostname: str, username: str, password: str) : 연결된 ssh를 가져오는 함수
	* selenium
		* get_status(driver) : 드라이버의 상태를 가져오는 함수
		* load_driver(chrome_options = None) : 드라이버를 생성하는 함수
		* load_driver2(port=9222) : 기존의 크롬드라이버를 사용하지 않고 일반 chrome.exe를 실행하는 함수
		* load_cache_driver(userId, chrome_options = None) : 캐시 드라이버를 생성하는 함수
		* n_login(driver: WebDriver, nid, pwd) : 네이버 로그인을 하는 함수
		* t_login(driver, tid, pwd) : 트위터 로그인을 하는 함수
		* daum_mail_login(driver, did, pwd) : 다음 로그인을 하는 함수
		* scrollDownUntilPageEnd(driver, SCROLL_PAUSE_SEC = 1) : 페이지 끝까지 스크롤을 내리는 함수
		* solve_reCAPTCHA(driver) : 구글 리캡차를 자동으로 푸는 함수
		* http_remove(link: str) : 링크에 http를 없애는 함수
		* http_append(link: str) : 링크에 http를 붙히는 함수
	* telegram
		* TelegramSender : 클래스
			* send(self, chat_id: str, text: str) : 텔레그램 메시지를 보내는 함수