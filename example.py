from xml_sql_converter import XMLSQLConverter

def main():
    # Crear instancia del convertidor
    converter = XMLSQLConverter()

    try:
        # Ejemplo de importación de XML a SQL
        print("Importando datos de XML a SQL...")
        converter.import_xml_to_sql('sample_data.xml', 'empleados')

        # Ejemplo de exportación de SQL a XML
        print("\nExportando datos de SQL a XML...")
        converter.export_sql_to_xml('empleados', 'exported_data.xml')

    finally:
        # Cerrar conexión
        converter.close_connection()

if __name__ == "__main__":
    main()
