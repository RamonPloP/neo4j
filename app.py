from flask import Flask, render_template, request, redirect, url_for, jsonify
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "abcd1234"   

driver = GraphDatabase.driver(uri, auth=(user, password))

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

#======================================================================================

@app.route('/dept')
def dept():
    data = {
        "title": "DEPT"
    }
    return render_template('dept.html', data=data)

@app.route('/dept/add', methods=['GET', 'POST'])
def addDept():
    data = {
        "title": "Agregar DEPT"
    }
    if request.method == 'POST':
        deptno = int(request.form['deptno'])
        dname = request.form['dname']
        loc = request.form['loc']

        with driver.session() as session:
            session.run("CREATE (d:DEPT {deptno: $deptno, dname: $dname, loc: $loc})", deptno=deptno, dname=dname, loc=loc)
        return redirect(url_for('addDept'))

    return render_template('./dept/add.html', data=data)

@app.route('/dept/list')
def listDept():
    with driver.session() as session:
        result = session.run("MATCH (d:DEPT) RETURN d.deptno as deptno, d.dname as dname, d.loc as loc")
        departments = [record for record in result]

    data = {
        "title": "Listar Dept",
        "departments": departments
    }

    return render_template('./dept/list.html', data=data)

@app.route('/dept/edit', methods=['GET', 'POST'])
def editDept():
    data = {
        "title": "Editar Dept"
    }

    with driver.session() as session:
        result = session.run("MATCH (d:DEPT) RETURN d.deptno as deptno, d.dname as dname, d.loc as loc")
        departments = [record for record in result]

    data["departments"] = departments

    if request.method == 'POST':
        deptno_to_edit = int(request.form['deptno'])
        new_dname = request.form['new_dname']
        new_loc = request.form['new_loc']

        with driver.session() as session:
            session.run("MATCH (d:DEPT {deptno: $deptno}) SET d.dname = $new_dname, d.loc = $new_loc", deptno=deptno_to_edit, new_dname=new_dname, new_loc=new_loc)

        return redirect(url_for('editDept'))

    return render_template('./dept/edit.html', data=data)

@app.route('/dept/del', methods=['GET','POST'])
def delDept():
    data = {
        "title": "Eliminar Dept"
    }

    with driver.session() as session:
        result = session.run("MATCH (d:DEPT) RETURN d.deptno as deptno, d.dname as dname, d.loc as loc")
        departments = [record for record in result]

    data["departments"] = departments

    if request.method == 'POST':
        deptno_to_delete = int(request.form['deptno'])

        with driver.session() as session:
            # Eliminar el departamento y sus relaciones
            session.run("MATCH (d:DEPT {deptno: $deptno}) DETACH DELETE d", deptno=deptno_to_delete)

        return redirect(url_for('delDept'))

    return render_template('./dept/del.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
    driver.close()