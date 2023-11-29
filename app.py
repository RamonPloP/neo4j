from flask import Flask, render_template, request, redirect, url_for, flash
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from datetime import datetime

uri = "bolt://localhost:7687"
user = "neo4j"
password = "abcd1234"   

driver = GraphDatabase.driver(uri, auth=(user, password))

app = Flask(__name__)
app.secret_key = 'BDA'

@app.route('/')
def index():
    data = {
        "title": "NEO4J"
    }
    return render_template('layout.html', data=data)

@app.route('/emp')
def emp():
    data = {
        "title": "EMP"
    }
    return render_template('emp.html', data=data)

@app.route('/emp/add', methods=['GET', 'POST'])
def addEmp():
    with driver.session() as session:
        result = session.run("MATCH (d:DEPT) RETURN d.deptno as deptno, d.dname as dname, d.loc as loc")
        departments = [record for record in result]

    with driver.session() as session:
        result = session.run("MATCH (e:EMP) RETURN e.empno as empno, e.ename as ename, e.job as job")
        employees = [record for record in result]

    data = {
        "title": "Agregar Emp",
        "departments": departments,
        "employees": employees
    }

    if request.method == 'POST':
        empno = int(request.form['empno'])
        ename = request.form['ename']
        job = request.form['job']
        mgr = int(request.form.get('mgr', -1))
        
        hiredate_str = request.form.get('hiredate', '')
        hiredate = datetime.strptime(hiredate_str, '%Y-%m-%d') if hiredate_str else None
        
        sal = float(request.form.get('sal', 0.0))
        comm = float(request.form.get('comm', 0.0))
        deptno = int(request.form.get('deptno', -1))

        with driver.session() as session:
            result = session.run("MATCH (e:EMP {empno: $empno}) RETURN e", empno=empno)
            existing_employee = result.single()

            if existing_employee:
                #El número de empleado ya está en uso
                return redirect(url_for('addEmp'))

        if mgr == empno:
            #Un empleado no puede ser su propio gerente
            return redirect(url_for('addEmp'))      

        with driver.session() as session:
            # Crear el nodo del nuevo empleado
            session.run(
                "CREATE (e:EMP {empno: $empno, ename: $ename, job: $job, hiredate: $hiredate, sal: $sal, comm: $comm})",
                empno=empno, ename=ename, job=job, hiredate=hiredate, sal=sal, comm=comm
            )

            # Si se proporciona un departamento, establecer la relación TRABAJA_EN
            if deptno != -1:
                session.run(
                    "MATCH (e:EMP {empno: $empno}), (d:DEPT {deptno: $deptno}) "
                    "CREATE (e)-[:TRABAJA_EN]->(d)",
                    empno=empno, deptno=deptno
                )

            # Si se proporciona un gerente, establecer la relación ES_GERENTE_DE
            if mgr != -1:
                session.run(
                    "MATCH (e:EMP {empno: $empno}), (m:EMP {empno: $mgr}) "
                    "CREATE (m)-[:ES_GERENTE_DE]->(e)",
                    empno=empno, mgr=mgr
                )

        return redirect(url_for('addEmp'))
    
    return render_template('./emp/add.html', data=data)


@app.route('/emp/list')
def listEmp():
    with driver.session() as session:
        result = session.run("MATCH (e:EMP) RETURN e.empno as empno, e.ename as ename, e.job as job")
        employees = [record for record in result]

    data = {
        "title": "Listar Emp",
        "employees": employees
    }
    return render_template('./emp/list.html', data=data)

@app.route('/emp/edit', methods=['GET', 'POST'])
def editEmp():
    with driver.session() as session:
        result = session.run("MATCH (d:DEPT) RETURN d.deptno as deptno, d.dname as dname, d.loc as loc")
        departments = [record for record in result]

    with driver.session() as session:
        result = session.run("MATCH (e:EMP) RETURN e.empno as empno, e.ename as ename, e.job as job")
        employees = [record for record in result]

    data = {
        "title": "Editar Emp",
        "departments": departments,
        "employees": employees
    }

    with driver.session() as session:
        result = session.run("MATCH (e:EMP) RETURN e.empno as empno, e.ename as ename, e.job as job, e.mgr as mgr, e.hiredate as hiredate, e.sal as sal, e.comm as comm, e.deptno as deptno")
        employees = [record for record in result]
        data["employees"] = employees

        if request.method == 'POST':
            empno_to_edit = int(request.form['empno'])
            new_ename = request.form['new_ename']
            new_job = request.form['new_job']
            new_mgr = int(request.form.get('new_mgr', -1))
            new_hiredate_str = request.form.get('new_hiredate', '')
            new_hiredate = datetime.strptime(new_hiredate_str, '%Y-%m-%d') if new_hiredate_str else None
            new_sal = float(request.form.get('new_sal', 0.0))
            new_comm = float(request.form.get('new_comm', 0.0))
            new_deptno = int(request.form.get('new_deptno', -1))

            with driver.session() as session:
                # Eliminar relaciones existentes
                session.run(
                    "MATCH (e:EMP {empno: $empno})-[r:TRABAJA_EN]->() DELETE r",
                    empno=empno_to_edit
                )
                session.run(
                    "MATCH (e:EMP {empno: $empno})<-[r:ES_GERENTE_DE]-() DELETE r",
                    empno=empno_to_edit
                )

                # Crear nuevas relaciones y actualizar propiedades del empleado
                session.run(
                    "MATCH (e:EMP {empno: $empno}), (d:DEPT {deptno: $new_deptno}), (mgr:EMP {empno: $new_mgr}) "
                    "CREATE (e)-[:TRABAJA_EN]->(d), (mgr)-[:ES_GERENTE_DE]->(e) "
                    "SET e.ename = $new_ename, e.job = $new_job, e.hiredate = $new_hiredate, e.sal = $new_sal, e.comm = $new_comm, e.deptno = $new_deptno",
                    empno=empno_to_edit, new_ename=new_ename, new_job=new_job, new_mgr=new_mgr, new_hiredate=new_hiredate, new_sal=new_sal, new_comm=new_comm, new_deptno=new_deptno
                )

            return redirect(url_for('editEmp'))

    return render_template('./emp/edit.html', data=data)


@app.route('/emp/del', methods=['GET','POST'])
def delEmp():
    data = {
        "title": "Eliminar Emp"
    }

    with driver.session() as session:
        result = session.run("MATCH (e:EMP) RETURN e.empno as empno, e.ename as ename, e.job as job")
        employees = [record for record in result]

    data["employees"] = employees

    if request.method == 'POST':
        empno_to_delete = int(request.form['empno'])

        with driver.session() as session:
            # Eliminar el empleado y sus relaciones
            session.run("MATCH (e:EMP {empno: $empno}) DETACH DELETE e", empno=empno_to_delete)

        return redirect(url_for('delEmp'))
    
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