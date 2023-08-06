re_date_list = [
    "\d{1,2}[\-/]\d{2,4}",
    "\d{1,2}\sgiờ",
    "năm\s\d{2,4}",
    "\d{1,2}h\d{1,2}[p]*",
    "\d{1,2}h\d{1,2}[p]*-\d{1,2}h\d{1,2}[p]*",
    "(ngày|tháng|tới|đến|mùng|ngày mùng) \d{1,2}[\-/]\d{1,4}",
    "(ngày|mùng|ngày mùng)\s\d{1,2}",
    "(ngày|mùng|ngày mùng)\s(một|hai|ba|tư|bốn|năm|nhăm|sáu|bẩy|bảy|tám|chín|mười)",
    "\d{4}[\-/]\d{2}[\-/]\d{2}",  # 2017-05-08T17:57:00
    "\d{4}[\-/]\d{2}[\-/]\d{2}t\d{2}:\d{2}:\d{2}",  # 2017-05-08T17:57:00
    "\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{1,4}",
    "(ngày|sáng|chiều|tối)\s\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{1,4}",
    "(ngày|sáng|chiều|tối)\s\d{1,2}[\-/\.]\d{1,2}",
    "tháng\s(một|hai|ba|tư|bốn|năm|nhăm|sáu|bẩy|bảy|tám|chín|mười|mười một|mười hai)",
    "tháng\s\d{1,2}",
    # "\d{1,2}-\d{1,2}/\d{1,2}",
]
