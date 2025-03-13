from lxml import etree
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from datetime import datetime

class XMLValidator:
    @staticmethod
    def validate_with_xsd(xml_file: str, xsd_file: str) -> bool:
        try:
            xml_doc = etree.parse(xml_file)
            xsd_doc = etree.parse(xsd_file)
            schema = etree.XMLSchema(xsd_doc)
            return schema.validate(xml_doc)
        except Exception as e:
            print(f"Error en la validación: {e}")
            return False

class XMLDataTypeConverter:
    @staticmethod
    def detect_type(value: str) -> tuple:
        try:
            # Intentar convertir a entero
            int_val = int(value)
            return ('INT', int_val)
        except ValueError:
            try:
                # Intentar convertir a float
                float_val = float(value)
                return ('FLOAT', float_val)
            except ValueError:
                try:
                    # Intentar convertir a fecha
                    date_val = datetime.strptime(value, '%Y-%m-%d')
                    return ('DATE', value)
                except ValueError:
                    # Si no es ninguno, devolver como VARCHAR
                    return ('VARCHAR(255)', value)

class XMLSQLConverter:
    def __init__(self):
        load_dotenv()
        self.connection = None
        self.validator = XMLValidator()
        self.type_converter = XMLDataTypeConverter()
        self.connect_to_database()

    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'test_db')
            )
        except Error as e:
            print(f"Error conectando a MySQL: {e}")
            raise

    def _process_complex_element(self, element: etree._Element) -> Dict[str, Any]:
        """Procesa un elemento XML complejo con atributos y subelementos."""
        data = dict(element.attrib)
        
        # Procesar subelementos
        for child in element:
            if len(child) > 0 or child.attrib:
                # Si el hijo tiene subelementos o atributos, procesarlo recursivamente
                data[child.tag] = self._process_complex_element(child)
            else:
                # Si es un elemento simple, guardar su valor
                data[child.tag] = child.text or ''
                
        return data

    def _create_table_for_complex_data(self, table_name: str, data: Dict[str, Any], cursor) -> None:
        """Crea una tabla SQL basada en datos complejos."""
        columns = []
        for key, value in data.items():
            if isinstance(value, dict):
                # Crear tabla relacionada para datos anidados
                related_table = f"{table_name}_{key}"
                self._create_table_for_complex_data(related_table, value, cursor)
                columns.append(f"{key}_id INT")
            else:
                # Detectar tipo de dato
                data_type, _ = self.type_converter.detect_type(str(value))
                columns.append(f"{key} {data_type}")

        columns_sql = ", ".join(columns)
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            {columns_sql}
        )
        """
        cursor.execute(create_table_query)

    def import_xml_to_sql(self, xml_file: str, table_name: str, xsd_file: Optional[str] = None) -> None:
        """Importa datos XML a SQL con soporte para estructuras complejas y validación XSD."""
        try:
            # Validar XML si se proporciona XSD
            if xsd_file and not self.validator.validate_with_xsd(xml_file, xsd_file):
                raise ValueError("El archivo XML no cumple con el esquema XSD")

            tree = etree.parse(xml_file)
            root = tree.getroot()
            
            # Manejar namespaces
            namespaces = root.nsmap
            
            cursor = self.connection.cursor()
            
            for element in root:
                data = self._process_complex_element(element)
                self._create_table_for_complex_data(table_name, data, cursor)
                
                # Insertar datos
                columns = list(data.keys())
                values = []
                for key, value in data.items():
                    if isinstance(value, dict):
                        # Manejar datos anidados
                        related_table = f"{table_name}_{key}"
                        cursor.execute(f"INSERT INTO {related_table} SET {', '.join([f'{k}=%s' for k in value.keys()])}", 
                                    list(value.values()))
                        values.append(cursor.lastrowid)
                    else:
                        values.append(value)

                placeholders = ", ".join(["%s"] * len(values))
                insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(insert_query, values)

            self.connection.commit()
            print(f"Datos importados exitosamente a la tabla {table_name}")

        except Exception as e:
            self.connection.rollback()
            print(f"Error durante la importación: {e}")
            raise

    def export_sql_to_xml(self, table_name: str, xml_file: str, root_element: str = "data") -> None:
        """Exporta datos SQL a XML con soporte para estructuras complejas."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Crear estructura XML con namespace opcional
            nsmap = {"xsi": "http://www.w3.org/2001/XMLSchema-instance"}
            root = etree.Element(root_element, nsmap=nsmap)
            
            # Obtener datos de la tabla principal
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            for row in rows:
                record = etree.SubElement(root, "record")
                
                for key, value in row.items():
                    if key == 'id':
                        continue
                        
                    if isinstance(value, (int, float)):
                        record.set(key, str(value))
                    elif isinstance(value, datetime):
                        record.set(key, value.strftime('%Y-%m-%d'))
                    else:
                        record.set(key, str(value) if value is not None else '')
                
                # Buscar datos relacionados en tablas hijo
                self._add_related_data(cursor, table_name, row['id'], record)

            # Guardar archivo XML
            tree = etree.ElementTree(root)
            tree.write(xml_file, pretty_print=True, xml_declaration=True, encoding='utf-8')
            print(f"Datos exportados exitosamente a {xml_file}")

        except Error as e:
            print(f"Error durante la exportación: {e}")
            raise

    def _add_related_data(self, cursor, parent_table: str, parent_id: int, parent_element: etree._Element) -> None:
        """Añade datos relacionados al XML."""
        # Buscar tablas relacionadas
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM information_schema.TABLES 
            WHERE TABLE_NAME LIKE %s
        """, (f"{parent_table}_%",))
        
        related_tables = cursor.fetchall()
        
        for table in related_tables:
            related_table = table['TABLE_NAME']
            cursor.execute(f"SELECT * FROM {related_table} WHERE {parent_table}_id = %s", (parent_id,))
            related_rows = cursor.fetchall()
            
            for row in related_rows:
                related_element = etree.SubElement(parent_element, related_table.split('_')[1])
                for key, value in row.items():
                    if key not in ('id', f'{parent_table}_id'):
                        related_element.set(key, str(value) if value is not None else '')

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
