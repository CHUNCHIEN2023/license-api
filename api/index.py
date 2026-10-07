from flask import Flask, request, jsonify
from supabase import create_client

app = Flask(__name__)

# 填入你剛才在 Supabase 拿到的 2 串資料
SUPABASE_URL = "https://qsbwtkbzsfhbvofdbuet.supabase.co/rest/v1/"  # 換成你的 Project URL
SUPABASE_KEY = "sb_publishable_zAc0dtU7lq982QE3vi-I8w_5B-6TKC5"  # 換成你的 Publishable Key

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json or {}
    key = data.get('license_key', '').strip()
    hwid = data.get('hwid', '').strip()

    if not key or not hwid:
        return jsonify({"valid": False, "message": "缺少序號或電腦識別碼"}), 400

    try:
        # 查詢序號是否存在
        res = supabase.table('licenses').select('*').eq('license_key', key).execute()
        if not res.data:
            return jsonify({"valid": False, "message": "序號不存在或不正確"}), 404

        record = res.data[0]

        # 情況 A：序號已被使用，比對 HWID 是否符合
        if record.get('is_used'):
            if record.get('hwid') == hwid:
                return jsonify({"valid": True, "message": "驗證成功（已綁定本機）"})
            else:
                return jsonify({"valid": False, "message": "此序號已在其他電腦開通綁定"}), 403

        # 情況 B：序號尚未被使用 ➔ 進行第一次綁定
        supabase.table('licenses').update({
            'is_used': True,
            'hwid': hwid
        }).eq('license_key', key).execute()

        return jsonify({"valid": True, "message": "開通綁定成功！"})

    except Exception as e:
        return jsonify({"valid": False, "message": f"伺服器錯誤: {str(e)}"}), 500

if __name__ == '__main__':
    app.run()