from flask import Flask, request, jsonify
# from flask_cors import CORS
from flask_cors import cross_origin
import json
app = Flask(__name__)
# CORS(app)

@app.route('/type', methods = ['GET'])
def gettype():
    f = open('typeofmaintenance.json')
    data = json.load(f)
    return data

@app.route('/item', methods = ['GET'])
def getitem():
    f = open('bahanransum.json')
    data = json.load(f)
    return data

@app.route('/calculatemulti', methods = ['POST'])
@cross_origin()
def calculatemulti() :
    headers = request.json['head']
    dummyItems = request.json['item']
    result = []
    for header in headers:
        bobot = header['dmi']
        wransum = header['weight']*bobot/100
        p_tdn = header['tdn'] / wransum*100
        p_cp = header['cp'] / wransum*100
        p_ca = header['ca'] / wransum*100
        p_p = header['p'] / wransum*100
        # Import required libraries
        from scipy.optimize import linprog

        tdn = [0.0]
        cp = [0.0]
        ca = [0.0]
        p = [0.0]
        c = [0]
        bound = []
        for item in dummyItems:
            tdn.append(-item['tdn']*item['bk'])
            cp.append(-item['cp']*item['bk'])
            ca.append(-item['ca']*item['bk'])
            p.append(-item['p']*item['bk'])
            c.append(item['harga'])
            bound.append((item['minpercentage']/100,item['maxpercentage']/100))
        tdn.pop(0)
        cp.pop(0)
        ca.pop(0)
        p.pop(0)
        c.pop(0)
        A = [cp, tdn, ca, p]

        # Set the inequality constraints vector
        b_out = [-p_cp, -p_tdn, -p_ca, -p_p]
        b = [-int(p_cp), -int(p_tdn), -int(p_ca), -int(p_p)]

        # Set the coefficients of the linear objective function vector
        A_eq = [[1]*len(dummyItems)]
        b_eq = [1]

        # Solve linear programming problem
        res = linprog(c, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=b_eq, bounds=bound, method='highs-ipm')

        data_hasil = {}
        if (res.fun != None):
            persen = []
            for i in range (len(res.x)):
                persen.append(res.x[i])
            # hasil.append(persen)
            data_hasil['percentage'] = persen
        data_hasil['wransum'] = wransum
        data_hasil['nutrition'] = b_out
        data_hasil['price'] = res.fun
        result.append(data_hasil)
    return jsonify(result)

@app.route('/calculatecustom', methods = ['POST'])
@cross_origin()
def calculatecustom() :
    header = request.json['head']
    dummyItems = request.json['item']

    # Import required libraries
    from scipy.optimize import linprog

    tdn = [0.0]
    cp = [0.0]
    ca = [0.0]
    p = [0.0]
    c = [0]
    bound = []
    for item in dummyItems:
        tdn.append(-item['tdn']*item['bk'])
        cp.append(-item['cp']*item['bk'])
        ca.append(-item['ca']*item['bk'])
        p.append(-item['p']*item['bk'])
        c.append(item['harga'])
        bound.append((item['minpercentage']/100,item['maxpercentage']/100))
    tdn.pop(0)
    cp.pop(0)
    ca.pop(0)
    p.pop(0)
    c.pop(0)
    A = [cp, tdn, ca, p]

    # Set the inequality constraints vector
    b = [-header['pk'], -header['tdn'], -header['ca'], -header['p']]

    # Set the coefficients of the linear objective function vector
    A_eq = [[1]*len(dummyItems)]
    b_eq = [1]

    # Solve linear programming problem
    res = linprog(c, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=b_eq, bounds=bound, method='highs-ipm')
    
    # hasil = []
    # hasil.append(res.fun)
    if (res.fun != None):
        persen = []
        for i in range (len(res.x)):
            persen.append(res.x[i])
        # hasil.append(persen)
    data_hasil = {}

    data_hasil['price'] = res.fun
    data_hasil['percentage'] = persen
    return jsonify(data_hasil)

if __name__ == '__main__' :
    app.run(debug=True)