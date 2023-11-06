import socket
import sys
import time
import threading
import os
from socket import timeout

# Hàm đọc cấu hình từ file
def read_config(file_config):
    config = {}
    with open(file_config, "r") as file:
        for line in file:
            key, value = line.strip().split("=")
            # strip(): loại bỏ khoảng trắng. 
            # split(): cắt bởi dấu = 
            config[key.strip()] = value.strip()
            # thêm cặp key-value vào config 
    return config


# Hàm kiểm tra ảnh
def is_image(url):
    url_str = url.decode()
    file_name = os.path.basename(url_str)
    if '.' in file_name:
        test = file_name.split('.')[1]
        return test in ["jpg", "png", "ico", "gif", "jpeg", "svg", "bmp", "tiff", "webp"]
    return False


# Hàm kiểm tra và xóa dữ liệu hết hạn trong cache
def clean_expired_cache(cache_folder, cache_time):
    current_time = time.time()

    for root, dirs, files in os.walk(cache_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_modified_time = os.path.getmtime(file_path)

            if current_time - file_modified_time > cache_time:
                try:
                    os.remove(file_path)
                    print(f"Removed expired cache file: {file_path}")
                except Exception as e:
                    print(f"Error while removing cache file {file_path}: {e}")


# Hàm lưu dữ liệu và tạo thư mục domain
def image_cache(domain, url, image_data, cache_time):
    url_str = url.decode()
    file_name = os.path.basename(url_str)
    cache_folder = "cache"
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
        
    web_folder = os.path.join(cache_folder, domain)
    if not os.path.exists(web_folder):
        os.makedirs(web_folder)
    new_image = os.path.join(web_folder, file_name)
    with open(new_image, "wb") as file:
        file.write(image_data)
        
    clean_expired_cache(cache_folder, cache_time)
        
      
# Hàm kiểm tra thời gian cho phép truy cập
def is_allowed_time(allowed_time_list):
    current_time = time.localtime()
    current_hour, current_minute, current_second = current_time.tm_hour, current_time.tm_min, current_time.tm_sec
    for allowed_time in allowed_time_list:
        start_hour, end_hour = map(int, allowed_time.split("-"))
        start_minute, start_second, end_minute, end_second = 0, 0, 0, 0
        if (start_hour < current_hour < end_hour) or (start_hour == current_hour and start_minute <= current_minute < end_minute) or (start_hour == current_hour and start_minute == current_minute and start_second <= current_second <= end_second):
            return True
    return False


# Hàm kiểm tra phương thức GET, POST, HEAD
def is_method(request_method):
    method = request_method.decode() if isinstance(request_method, bytes) else request_method
    return method in ["GET", "POST", "HEAD"]


# Hàm kiểm tra tên miền trong whitelist
def is_whitelisted(domain, whitelist):
    decoded_domain = domain.decode() if isinstance(domain, bytes) else domain
    for item in whitelist:
        decoded_item = item.decode() if isinstance(item, bytes) else item
        if decoded_domain == decoded_item:
            return True
    return False


# Phân tích yêu cầu và xác định phương thức
def parse_request(message):
    request_parts = message.split(b"\r\n")[0]
    request_method, request_url, _ = request_parts.split(b" ")
    return request_method, request_url


def content_length(response_data):
    if b"Content-Length:" in response_data:
        content_length_pos = response_data.find(b"Content-Length:")
        end_of_content_length = response_data.find(b"\r\n", content_length_pos)
        content_length = int(response_data[content_length_pos + len(b"Content-Length:"):end_of_content_length])
        if len(response_data) - end_of_content_length >= content_length:
            return content_length
    return None


def chunked_data(response_data, client_socket):
    if b"Transfer-Encoding: chunked" in response_data:
        # Tìm vị trí của dòng kết thúc chunk trước (có thể là \r\n hoặc \n)
        chunk_end_pos = response_data.find(b"\r\n\r\n")
        if chunk_end_pos == -1:
            chunk_end_pos = response_data.find(b"\n\n")
        if chunk_end_pos != -1:
            # Lấy dữ liệu chunk sau dòng kết thúc chunk
            chunk_data = response_data[chunk_end_pos+4:]
            # Gửi dữ liệu chunk cho client
            client_socket.send(chunk_data)
      

# Hàm tách phần body repsonse truyền về để lưu ảnh
def extract_response_content(response_data):
    content_start = response_data.find(b'\r\n\r\n') + 4
    return response_data[content_start:]
      

# Gửi dữ liệu từ server tới máy client
def send_data_to_client(response_data, client_socket, server, request_url, target_host, cache_time):
    while True:
        server.settimeout(1)
        try:
            data_recv = server.recv(4096)
            if len(data_recv) == 0:
                print("No data received from server\r\n")
                break
            else:
                response_data += data_recv
                client_socket.send(data_recv)
                
                # Xử lý trường hợp Content-Length
                content_len = content_length(response_data)
                if content_len is not None and len(response_data) >= content_len:
                    break
                
                # Xử lý trường hợp "Transfer-Encoding: chunked"
                chunked_data(response_data, client_socket)
        except timeout:
            break
        
    if is_image(request_url):
        image_cache(target_host.decode(), request_url, extract_response_content(response_data), cache_time)    


def _extracted_from_handle_get_method_6(request_url, target_folder, client_socket):
    url_str = request_url.decode()
    file_name = os.path.basename(url_str)
    temp = file_name.split('.')
    temp01 = temp[1]
    content_type = ""
    content_type = "image/x-icon" if (temp01 == "ico") else "image/png"
    image_path = os.path.join(target_folder, file_name)
    if os.path.exists(image_path):
        with open(image_path, "rb") as file:
            res_data = file.read()
            client_socket.sendall(res_data)
            print("Send data from cache proxy")


# Xử lý phương thứ GET
def handle_get_method(client_socket, server, request_url, target_host, cache_time):
    if is_image(request_url):
        target_host_str = target_host.decode()
        target_folder = os.path.join("cache", target_host_str)
        if os.path.exists(target_folder) and os.path.isdir(target_folder):
            _extracted_from_handle_get_method_6(request_url, target_folder, client_socket)
                    
    response_data = b""
    send_data_to_client(response_data, client_socket, server, request_url, target_host, cache_time)


# Xử lý phương thức POST
def handle_post_method(client_socket, server, request_url, target_host, cache_time):
    if is_image(request_url):
        target_host_str = target_host.decode()
        target_folder = os.path.join("cache", target_host_str)
        if os.path.exists(target_folder) and os.path.isdir(target_folder):
            _extracted_from_handle_get_method_6(request_url, target_folder, client_socket)
                    
    response_data = b""
    send_data_to_client(response_data, client_socket, server, request_url, target_host, cache_time)


# Xử lý phương thức HEAD
def handle_head_method(client_socket, server, request_url, target_host, cache_time):
    if is_image(request_url):
        target_host_str = target_host.decode()
        target_folder = os.path.join("cache", target_host_str)
        if os.path.exists(target_folder) and os.path.isdir(target_folder):
            _extracted_from_handle_get_method_6(request_url, target_folder, client_socket)
                    
    response_data = b""
    send_data_to_client(response_data, client_socket, server, request_url, target_host, cache_time)
    
    # Trích xuất header từ dữ liệu phản hồi
    headers_end = response_data.find(b"\r\n\r\n")
    headers = response_data[:headers_end] if headers != -1 else response_data
    client_socket.send(headers)


def send_response(client_socket, response):
    client_socket.sendall(response)
    client_socket.close()

def _extracted_from_forbidden_response_2(file_path, status_line, content_type_line):
    response = b""
    with open(file_path, "rb") as file:
        response = file.read()
    content_length_line = b"Content-Length: " + str(len(response)).encode() + b"\r\n"
    return status_line + content_type_line + content_length_line + b"\r\n" + response

def forbidden_response(client_socket):
    response_html_error = _extracted_from_forbidden_response_2(
        "Forbidden.html",
        b"HTTP/1.1 403 Forbidden\r\n",
        b"Content-Type: text/html\r\n",
    )
    
    full_response = response_html_error 

    send_response(client_socket, full_response)


def handle_client(client_socket, server, message, target_host, cache_time):
    server.sendall(message)
    
    request_method, request_url = parse_request(message)
    
    if is_method(request_method.decode()) == False:
        forbidden_response(client_socket)
        return
    
    if request_method == b"GET":
        handle_get_method(client_socket, server, request_url, target_host, cache_time)
    elif request_method == b"POST":
        handle_post_method(client_socket, server, request_url, target_host, cache_time)
    elif request_method == b"HEAD":
        response_data = handle_head_method(client_socket, server, request_url, target_host, cache_time)
    
    client_socket.close()


# Hàm nhận dữ liệu từ client_socket
def receive_data(client_socket):
    # Biến message được khởi tạo để chứa dữ liệu nhận được từ máy khách. Dữ liệu này là yêu cầu HTTP mà máy khách gửi tới proxy.
    message = b""
    # Vòng lặp này đọc dữ liệu từ client_socket bằng cách gọi recv() để nhận dữ liệu từ máy khách. 
    # Dữ liệu được gắn vào biến data.
    while True:
        data_recv = client_socket.recv(4096)
        message += data_recv
        if len(data_recv) < 4096:
            break
    return message


# Hàm trích xuất thông tin từ yêu  cầu HTTP
def extract_request_info(message):
    # Lấy dòng đầu tiên của yêu cầu HTTP.
    request_parts = message.split(b'\r\n')[0]
    # Tách URL từ dòng yêu cầu HTTP.
    url = request_parts.split(b" ")[1]
    http_pos = url.find(b"://")
    
    # Cổng mục tiêu mà ứng dụng proxy sẽ gửi yêu cầu tới. Mặc định là cổng 80, được sử dụng cho giao thức HTTP.
    target_port = 80
    
    temp = url if http_pos == -1 else url[(http_pos + 3):]
    target_hostpos = temp.find(b"/")
        
    if b":" in temp:
        portpos = temp.find(b":")

        target_port = (int(temp[(portpos + 1) :]) if target_hostpos == -1 else int(temp[(portpos + 1) : target_hostpos]))
        target_host = temp[:(portpos)]
    else:
        target_host = temp if target_hostpos == -1 else temp[:(target_hostpos)]
    
    tail = "" if target_hostpos == -1 else temp[(target_hostpos + 1):]
    
    return target_host, target_port, tail


# Hàm kết nối đến server
def connect_to_server(target_host, target_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((target_host, target_port))
    return server


# Hàm xử lý yêu cầu từ một client kết nối qua socket và chuyển tiếp yêu cầu đó đến một máy chủ server
def process(client_socket, client_address, allowed_time_list, whitelist, cache_time): 
    if is_allowed_time(allowed_time_list) == False:
        forbidden_response(client_socket)
        return
    
    try:
        if message := receive_data(client_socket):
            target_host, target_port, tail = extract_request_info(message)
            target_host_str = target_host.decode()
            print("HOST:", target_host_str)

            if not is_whitelisted(target_host, whitelist):
                forbidden_response(client_socket)
                return

            server = connect_to_server(target_host, target_port)
            handle_client(client_socket, server, message, target_host, cache_time)
    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()


# Hàm tạo socket cho máy chủ proxy
def create_proxy_server_socket(proxy_host, proxy_port):
    # Khởi tạo socket và lắng nghe kết nối
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind((proxy_host, proxy_port))
    proxy_socket.listen(5)
    
    return proxy_socket


def main():
    proxy_host = "127.0.0.1"  # Địa chỉ IP của proxy server
    proxy_port = 8888  # Cổng dịch vụ proxy
    
    proxy_socket = create_proxy_server_socket(proxy_host, proxy_port)
    
    print(f"Proxy server is listening on {proxy_host}:{proxy_port}")
    
    # Đọc cấu hình từ tệp "config.txt"
    config = read_config("config.txt")
    
    # Gán giá trị cấu hình cho các biến
    cache_time = int(config["cache_time"])
    whitelist = [domain.strip() for domain in config["whitelisting"].split(",")]
    allowed_time_list = config["time"].split(",")
    
    try:
        while True:
            client_socket, client_address = proxy_socket.accept()
            client_thread = threading.Thread(target=process, args=(client_socket, client_address, allowed_time_list, whitelist, cache_time))
            client_thread.start()
    except KeyboardInterrupt:
        client_socket.close()
        
        
if __name__ == "__main__":
    main()
    

# 1. http://oosc.online/
# 2. http://example.com/
# 3. http://www.google.com/
# 4. http://www.bing.com/
# 5. http://testphp.vulnweb.com/login.php (test POST, user/pass: test/test)
# 6. http://vbsca.ca/login/login.asp (test POST, user/pass: pmcmahon/somepass hoặc jbloggs/anotherpass)
# 7. http://vbsca.ca/login/
# 8. http://vbsca.ca/login/LoginsAndPermissions3.htm