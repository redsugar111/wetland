import math
from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os

app = Flask(__name__, template_folder='.', static_url_path='')
CORS(app)

def calculate_shape_index(params):
    """ 计算形状指数 (SI) 相关参数 """
    try:
        # 获取参数，如果没有则为 None
        P = params.get("P")
        A = params.get("A")
        SI = params.get("SI")

        # 转换非空值为浮点数
        P = float(P) if P else None
        A = float(A) if A else None
        SI = float(SI) if SI else None

        result = {"steps": []}

        if P and A:  # 已知周长和面积，计算形状指数
            SI = P / (2 * math.sqrt(math.pi * A))
            result["steps"].append(f"1. 代入公式：SI = P / (2√(πA))")
            result["steps"].append(f"2. 将数值代入：SI = {P} / (2√(π × {A}))")
            result["steps"].append(f"3. 计算结果：SI = {round(SI, 4)}")
            result["SI"] = round(SI, 4)
            result["P"] = P
            result["A"] = A

        elif SI and A:  # 已知形状指数和面积，计算周长
            P = SI * (2 * math.sqrt(math.pi * A))
            result["steps"].append(f"1. 代入公式：P = SI × 2√(πA)")
            result["steps"].append(f"2. 将数值代入：P = {SI} × 2√(π × {A})")
            result["steps"].append(f"3. 计算结果：P = {round(P, 2)} 米")
            result["P"] = round(P, 2)
            result["SI"] = SI
            result["A"] = A

        elif SI and P:  # 已知形状指数和周长，计算面积
            A = (P / (2 * SI)) ** 2 / math.pi
            result["steps"].append(f"1. 代入公式：A = (P / (2SI))² / π")
            result["steps"].append(f"2. 将数值代入：A = ({P} / (2 × {SI}))² / π")
            result["steps"].append(f"3. 计算结果：A = {round(A, 2)} 平方米")
            result["A"] = round(A, 2)
            result["SI"] = SI
            result["P"] = P

        else:
            return {"error": "请输入两个参数进行计算：\n- 周长(P)和面积(A)\n- 形状指数(SI)和面积(A)\n- 形状指数(SI)和周长(P)"}

        return result

    except ZeroDivisionError:
        return {"error": "计算过程中出现除以零的错误"}
    except ValueError as e:
        return {"error": "请输入有效的数值"}
    except Exception as e:
        return {"error": f"计算错误：{str(e)}"}

def calculate_rich_shoreline(params):
    try:
        # 获取输入参数
        L = float(params.get('L', 0))  # 岸线实际长度
        L0 = float(params.get('L0', 0))  # 最短距离
        A = float(params.get('A', 0))  # 面积
        
        # 验证输入
        if not L or not A:
            raise ValueError("请输入必要的参数：岸线实际长度(L)和面积(A)")

        result = {}
        steps = []

        # 1. 计算岸线发育系数 (DL)
        DL = L / (2 * math.sqrt(math.pi * A))
        result['DL'] = DL
        steps.append({
            'type': 'DL',
            'values': {
                'L': L,
                'A': A
            },
            'result': DL
        })

        # 2. 计算分形维数 (FD)
        if A > 0:
            FD = 2 * math.log(L) / math.log(A)
            result['FD'] = FD
            steps.append({
                'type': 'FD',
                'values': {
                    'L': L,
                    'A': A
                },
                'result': FD
            })

        # 3. 计算岸线密度 (D)
        D = L / A
        result['D'] = D
        steps.append({
            'type': 'D',
            'values': {
                'L': L,
                'A': A
            },
            'result': D
        })

        # 4. 计算岸线曲率 (C)
        if L0 > 0:
            C = L / L0
            result['C'] = C
            steps.append({
                'type': 'C',
                'values': {
                    'L': L,
                    'L0': L0
                },
                'result': C
            })

        # 添加输入参数到结果中
        result['L'] = L
        result['L0'] = L0
        result['A'] = A
        result['steps'] = steps

        # 打印调试信息
        print("计算结果:", result)
        
        return result

    except ValueError as e:
        print(f"ValueError: {str(e)}")
        return {"error": str(e)}
    except ZeroDivisionError:
        print("ZeroDivisionError")
        return {"error": "计算过程中出现除以零的错误"}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {"error": f"计算错误：{str(e)}"}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path == "":
        return render_template('index.html')
    return render_template('index.html')

@app.route('/api/calculate_shape_index', methods=['GET', 'POST'])
def api_shape_index():
    try:
        print("Received params:", request.args)
        result = calculate_shape_index(request.args)
        print("Calculation result:", result)
        return jsonify(result)
    except Exception as e:
        print(f"Error in calculation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/calculate_rich_shoreline', methods=['GET', 'POST'])
def api_shoreline():
    try:
        print("Received params:", request.args)
        result = calculate_rich_shoreline(request.args)
        print("Calculation result:", result)
        return jsonify(result)
    except Exception as e:
        print(f"Error in calculation: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 