from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    data = {
        "title": "NEO4J"
    }
    return render_template('layout.html', data=data);

@app.route('/emp')
def emp():
    data = {
        "title": "EMP"
    }
    return render_template('emp.html', data=data)

@app.route('/emp/add')
def addEmp():
    data = {
        "title": "Agregar Emp"
    }
    return render_template('./emp/add.html', data=data)

@app.route('/emp/list')
def listEmp():
    data = {
        "title": "Listar Emp"
    }
    return render_template('./emp/list.html', data=data)

@app.route('/emp/edit')
def editEmp():
    data = {
        "title": "Editar Emp"
    }
    return render_template('./emp/edit.html', data=data)

@app.route('/emp/del')
def delEmp():
    data = {
        "title": "Eliminar Emp"
    }
    return render_template('./emp/del.html', data=data)

@app.route('/dept')
def dept():
    data = {
        "title": "DEPT"
    }
    return render_template('dept.html', data=data)

@app.route('/dept/add')
def addDept():
    data = {
        "title": "Agregar DEPT"
    }
    return render_template('./dept/add.html', data=data)

@app.route('/dept/list')
def listDept():
    data = {
        "title": "Listar Dept"
    }
    return render_template('./dept/list.html', data=data)

@app.route('/dept/edit')
def editDept():
    data = {
        "title": "Editar Dept"
    }
    return render_template('./dept/edit.html', data=data)

@app.route('/dept/del')
def delDept():
    data = {
        "title": "Eliminar Dept"
    }
    return render_template('./dept/del.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)