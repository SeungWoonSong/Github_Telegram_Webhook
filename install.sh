#!/bin/bash

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 외부 IP 확인
get_external_ip() {
    external_ip=$(curl -s https://api.ipify.org)
    if [ -z "$external_ip" ]; then
        log_error "외부 IP를 확인할 수 없습니다."
        exit 1
    fi
    echo $external_ip
}

# 필수 환경 변수 확인
check_env_vars() {
    log_info "환경 변수 확인 중..."
    
    if [ ! -f .env ]; then
        log_error ".env 파일이 없습니다. 샘플 .env 파일을 생성합니다."
        cat > .env << EOL
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username
TELEGRAM_DEFAULT_CHAT_ID=your_default_chat_id
EVENT_CHAT_MAPPING={"push": "chat_id_1", "pull_request": "chat_id_2"}
SERVER_PORT=8080
DEVELOPMENT_MODE=false
EOL
        log_warn ".env 파일을 수정하여 필요한 값들을 설정해주세요."
        exit 1
    fi
}

# 도메인 확인
get_domain() {
    # .env 파일에서 SERVER_URL 읽기
    if [ -f .env ]; then
        SERVER_URL=$(grep "^SERVER_URL=" .env | cut -d '=' -f2)
        # 값이 있고 비어있지 않은 경우
        if [ ! -z "$SERVER_URL" ] && [ "$SERVER_URL" != '""' ] && [ "$SERVER_URL" != "''" ]; then
            echo $SERVER_URL
            return
        fi
    fi
    
    # SERVER_URL이 없거나 비어있는 경우 외부 IP 사용
    external_ip=$(get_external_ip)
    log_warn "SERVER_URL이 설정되지 않아 외부 IP($external_ip)를 도메인으로 사용합니다."
    log_warn "주의: 고정 IP가 아닌 경우, IP가 변경되면 SSL 인증서가 무효화되어 서비스가 중단될 수 있습니다."
    log_warn "      이 경우 install.sh를 다시 실행하여 새로운 IP로 SSL 인증서를 재발급받아야 합니다."
    log_warn "      고정 도메인을 사용하려면 .env 파일의 SERVER_URL을 설정하세요."
    echo $external_ip
}

# Python 가상환경 설정
setup_virtualenv() {
    log_info "Python 가상환경 설정 중..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3가 설치되어 있지 않습니다."
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3가 설치되어 있지 않습니다."
        exit 1
    }
    
    # 가상환경 생성
    python3 -m venv venv
    source venv/bin/activate
    
    # 의존성 설치
    pip install -r requirements.txt
}

# Nginx 설치 및 설정
setup_nginx() {
    log_info "Nginx 설치 및 설정 중..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y nginx
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install nginx
    else
        log_error "지원하지 않는 운영체제입니다."
        exit 1
    fi
    
    # Nginx 설정 파일 생성
    sudo tee /etc/nginx/sites-available/github_notifier << EOL
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOL
    
    # Nginx 설정 활성화
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo ln -s /etc/nginx/sites-available/github_notifier /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
    fi
    
    # Nginx 재시작
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl restart nginx
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services restart nginx
    fi
}

# SSL 인증서 설정 (Let's Encrypt)
setup_ssl() {
    log_info "SSL 인증서 설정 중..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Certbot 설치
        sudo apt-get install -y certbot python3-certbot-nginx
        
        # SSL 인증서 발급
        sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL
        
        # 인증서 자동 갱신 설정
        sudo systemctl enable certbot.timer
        sudo systemctl start certbot.timer
    else
        log_warn "SSL 인증서 설정은 Linux 환경에서만 지원됩니다."
    fi
}

# 서비스 자동 시작 설정
setup_service() {
    log_info "서비스 자동 시작 설정 중..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # systemd 서비스 파일 생성
        sudo tee /etc/systemd/system/github_notifier.service << EOL
[Unit]
Description=GitHub Notifier Telegram Bot
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL
        
        # 서비스 활성화 및 시작
        sudo systemctl enable github_notifier
        sudo systemctl start github_notifier
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # launchd plist 파일 생성
        tee ~/Library/LaunchAgents/com.github.notifier.telegram.plist << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.github.notifier.telegram</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(pwd)/venv/bin/python</string>
        <string>$(pwd)/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$(pwd)</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOL
        
        # 서비스 로드
        launchctl load ~/Library/LaunchAgents/com.github.notifier.telegram.plist
    fi
}

# 메인 설치 프로세스
main() {
    log_info "GitHub Notifier Telegram Bot 설치를 시작합니다..."
    
    # 1. 환경 변수 확인
    check_env_vars
    
    # 2. Python 가상환경 설정
    setup_virtualenv
    
    # 3. 도메인 설정
    DOMAIN=$(get_domain)
    
    # 4. 이메일 입력
    read -p "이메일을 입력하세요 (SSL 인증서 발급용): " EMAIL
    
    # 5. Nginx 설치 및 설정
    setup_nginx
    
    # 6. SSL 인증서 설정
    setup_ssl
    
    # 7. 서비스 자동 시작 설정
    setup_service
    
    log_info "설치가 완료되었습니다!"
    log_info "서비스 상태를 확인하려면 다음 명령어를 실행하세요:"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "sudo systemctl status github_notifier"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "launchctl list | grep github.notifier"
    fi
    
    log_info "웹훅 URL: https://$DOMAIN/webhook"
    
    if [ -z "$SERVER_URL" ]; then
        log_warn "GitHub 웹훅 설정 시 IP 주소가 변경되면 웹훅 URL도 변경해야 합니다."
        log_warn "안정적인 서비스를 위해 고정 도메인 사용을 권장합니다."
    fi
}

# 스크립트 실행
main
