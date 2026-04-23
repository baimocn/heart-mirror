from flask import request, jsonify, render_template
from models import get_donation_list, add_donation, get_donation_flows, add_donation_flow, get_donation_flow_by_id, update_donation_flow, delete_donation_flow, get_donation_batches, add_donation_batch, get_donation_batch_by_id, update_donation_batch, delete_donation_batch, update_batch_total_amount
from app import app, admin_required
import json
import random
import sqlite3
import os

@app.route('/api/donations', methods=['GET'])
def donations():
    return jsonify(get_donation_list())

@app.route('/api/donate', methods=['POST'])
def donate():
    """模拟捐款：直接确认，更新总额"""
    data = request.json
    device_id = data.get('device_id', '')
    nickname = data.get('nickname', '匿名用户')
    amount = float(data.get('amount', 1.0))
    if amount <= 0:
        return jsonify({'error': '金额必须大于0'}), 400
    add_donation(device_id, amount, nickname, status='confirmed')
    return jsonify({'status': 'ok', 'message': '感谢您的善意！'})

@app.route('/api/norms', methods=['GET'])
def get_norms():
    """获取群体平均数据"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'heart_mirror.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT total_users, sum_justice, sum_altruism, sum_rule, sum_empathy, sum_utilitarian, sum_punish 
                FROM global_norms WHERE id=1''')
    row = c.fetchone()
    conn.close()
    
    if not row or row[0] == 0:
        return jsonify({'avg': [50, 50, 50, 50, 50, 50], 'count': 0})
    
    total = row[0]
    avg = [row[1]/total, row[2]/total, row[3]/total, row[4]/total, row[5]/total, row[6]/total]
    return jsonify({'avg': avg, 'count': total})

@app.route('/api/flows', methods=['GET'])
def donation_flows_get():
    flows = get_donation_flows()
    return jsonify(flows), 200

@app.route('/api/flows', methods=['POST'])
@admin_required
def donation_flows_post():
    data = request.json
    batch_id = data.get('batch_id')
    amount = data.get('amount')
    purpose = data.get('purpose')
    date = data.get('date')
    description = data.get('description')
    images = json.dumps(data.get('images', []))
    
    flow_id = add_donation_flow(batch_id, amount, purpose, date, description, images)
    return jsonify({'message': '善款流向记录添加成功', 'id': flow_id}), 201

@app.route('/api/flows/<int:flow_id>', methods=['GET'])
def donation_flow_detail_get(flow_id):
    flow = get_donation_flow_by_id(flow_id)
    if flow:
        return jsonify(flow), 200
    return jsonify({'error': '记录不存在'}), 404

@app.route('/api/flows/<int:flow_id>', methods=['PUT', 'DELETE'])
@admin_required
def donation_flow_detail_modify(flow_id):
    if request.method == 'PUT':
        data = request.json
        amount = data.get('amount')
        purpose = data.get('purpose')
        date = data.get('date')
        description = data.get('description')
        images = json.dumps(data.get('images', []))
        
        update_donation_flow(flow_id, amount, purpose, date, description, images)
        return jsonify({'message': '善款流向记录更新成功'}), 200
    elif request.method == 'DELETE':
        delete_donation_flow(flow_id)
        return jsonify({'message': '善款流向记录删除成功'}), 200

@app.route('/api/batches', methods=['GET'])
def donation_batches_get():
    batches = get_donation_batches()
    return jsonify(batches), 200

@app.route('/api/batches', methods=['POST'])
@admin_required
def donation_batches_post():
    data = request.json
    batch_id = data.get('batch_id')
    name = data.get('name')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    description = data.get('description')
    images = json.dumps(data.get('images', []))
    
    batch_id = add_donation_batch(batch_id, name, start_date, end_date, description, images)
    return jsonify({'message': '善款批次添加成功', 'id': batch_id}), 201

@app.route('/api/batches/<string:batch_id>', methods=['GET'])
def donation_batch_detail_get(batch_id):
    batch = get_donation_batch_by_id(batch_id)
    if batch:
        return jsonify(batch), 200
    return jsonify({'error': '批次不存在'}), 404

@app.route('/api/batches/<string:batch_id>', methods=['PUT', 'DELETE'])
@admin_required
def donation_batch_detail_modify(batch_id):
    if request.method == 'PUT':
        data = request.json
        name = data.get('name')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        status = data.get('status')
        description = data.get('description')
        images = json.dumps(data.get('images', []))
        
        update_donation_batch(batch_id, name, start_date, end_date, status, description, images)
        return jsonify({'message': '善款批次更新成功'}), 200
    elif request.method == 'DELETE':
        delete_donation_batch(batch_id)
        return jsonify({'message': '善款批次删除成功'}), 200

@app.route('/api/batches/<string:batch_id>/update_amount')
@admin_required
def update_batch_amount(batch_id):
    update_batch_total_amount(batch_id)
    return jsonify({'message': '批次金额更新成功'}), 200

@app.route('/api/generate_story', methods=['POST'])
def generate_story():
    """生成公益故事"""
    data = request.json
    title = data.get('title', '道德守护者')
    amount = data.get('amount', 1.0)
    
    # 公益故事模板
    templates = [
        {
            'title': '温暖传递',
            'content': f'亲爱的{title}，您的{amount}元善款已经成为温暖的种子，在需要帮助的人心中生根发芽。每一分善意都在传递着希望，每一次付出都在点亮他人的生活。感谢您的善良，让世界变得更加美好。'
        },
        {
            'title': '爱心涟漪',
            'content': f'尊敬的{title}，您的{amount}元善款如同投入湖面的石子，激起了爱的涟漪。这份善意将帮助那些处于困境中的人们，让他们感受到社会的温暖。您的行动是对人性美好的最好诠释。'
        },
        {
            'title': '希望之光',
            'content': f'亲爱的{title}，您的{amount}元善款是黑暗中的一束光，为需要帮助的人带来了希望。您的善良不仅是物质上的支持，更是精神上的鼓励。感谢您用行动诠释了什么是真正的道德。'
        },
        {
            'title': '善的力量',
            'content': f'尊敬的{title}，您的{amount}元善款展现了善的力量。这份力量将帮助那些需要帮助的人，让他们感受到人间的温情。您的行动是对道德最好的实践，是对社会最美好的贡献。'
        },
        {
            'title': '爱的传递',
            'content': f'亲爱的{title}，您的{amount}元善款是爱的传递。这份爱将温暖那些需要帮助的人，让他们感受到社会的关怀。您的善良是社会的正能量，是我们学习的榜样。'
        }
    ]
    
    # 随机选择一个模板
    story = random.choice(templates)
    
    return jsonify(story), 200

@app.route('/flows')
def flows():
    return render_template('flows.html')

@app.route('/admin/flows')
@admin_required
def admin_flows():
    return render_template('admin_flows.html')

@app.route('/admin/batches')
@admin_required
def admin_batches():
    return render_template('admin_batches.html')
