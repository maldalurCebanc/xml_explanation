from lxml import etree
from basex import BaseXClient
import os

# Cargar el archivo XML
xml_file = 'empleados_complejos.xml'
tree = etree.parse(xml_file)
root = tree.getroot()

def ejecutar_xpath():
    print("\n=== Ejemplos de XPath ===")
    
    # 1. Obtener todos los empleados
    print("\n1. Lista de todos los empleados:")
    empleados = root.xpath("//empleado")
    for emp in empleados:
        print(f"ID: {emp.get('id_empleado')}")

    # 2. Obtener nombres de empleados con salario > 40000
    print("\n2. Empleados con salario > 40000:")
    empleados_salario = root.xpath("//empleado[datos_laborales/@salario > 40000]/datos_personales/@nombre")
    for nombre in empleados_salario:
        print(nombre)

    # 3. Empleados del departamento IT
    print("\n3. Empleados en IT:")
    empleados_it = root.xpath("//empleado[datos_laborales/@departamento='IT']/datos_personales/@nombre")
    for nombre in empleados_it:
        print(nombre)

    # 4. Contar número total de empleados
    total_empleados = root.xpath("count(//empleado)")
    print(f"\n4. Total de empleados: {total_empleados}")

    # 5. Promedio de salarios
    salarios = root.xpath("//datos_laborales/@salario")
    promedio = sum(float(s) for s in salarios) / len(salarios)
    print(f"\n5. Promedio de salarios: {promedio:.2f}")

def ejecutar_xquery():
    print("\n=== Ejemplos de XQuery ===")
    
    try:
        # Crear una sesión de BaseX
        session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
        
        # 1. Listar empleados con formato personalizado
        xquery1 = """
        for $emp in doc("empleados_complejos.xml")//empleado
        return concat(
            "Empleado: ", 
            $emp/datos_personales/@nombre, 
            " ", 
            $emp/datos_personales/@apellidos,
            " - Departamento: ",
            $emp/datos_laborales/@departamento
        )
        """
        
        # 2. Resumen de departamentos y salarios
        xquery2 = """
        for $dept in distinct-values(doc("empleados_complejos.xml")//datos_laborales/@departamento)
        let $emp_dept := doc("empleados_complejos.xml")//empleado[datos_laborales/@departamento=$dept]
        return concat(
            "Departamento: ", $dept,
            ", Empleados: ", count($emp_dept),
            ", Salario promedio: ", 
            avg($emp_dept/datos_laborales/@salario)
        )
        """
        
        print("\n1. Listado de empleados:")
        print(session.execute(xquery1))
        
        print("\n2. Resumen por departamentos:")
        print(session.execute(xquery2))
        
    except Exception as e:
        print(f"Error al ejecutar XQuery: {e}")
        print("Nota: Asegúrate de tener BaseX Server ejecutándose localmente")
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    print("Demostración de XPath y XQuery")
    ejecutar_xpath()
    # ejecutar_xquery()
