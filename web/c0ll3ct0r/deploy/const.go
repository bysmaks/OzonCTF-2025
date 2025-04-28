package main

import "os"

var JWT_SECRET = []byte(os.Getenv("JWT_SECRET"))
var BLOCKED_PROTOCOLS = []string{"DICT", "FILE", "FTP", "FTPS", "IMAP", "IMAPS", "LDAP", "LDAPS", "MQTT", "POP3",
	"POP3S", "RTMP", "RTMPS", "RTSP", "SCP", "SFTP", "SMB", "SMBS", "SMTP", "SMTPS", "TELNET", "TFTP", "WS", "WSS"}
var ALLOWED_STATUS_CODES = []int{200, 301, 302, 307}
var FLAG = os.Getenv("FLAG")
