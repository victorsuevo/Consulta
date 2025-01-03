import sqlite3
import shutil
import os
import pandas as pd
from datetime import datetime, timedelta
import time
import customtkinter as tk
import sys
from tkinter import Checkbutton, IntVar, Label, Entry, Button, messagebox, Toplevel, Text, END
class ClinicaPediatrica:
    def __init__(self):
        self.conn = sqlite3.connect('clinica.db')
        self.cursor = self.conn.cursor()
        self.dateFormat = "%d/%m/%Y"
        self.timeFormat = "%H:%M"
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS pacientes
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              nome TEXT NOT NULL,
                              idade INTEGER NOT NULL,
                              endereco TEXT NOT NULL,
                              telefone TEXT,
                              CPF TEXT NOT NULL)''')
        self.conn.commit()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS consultas
                                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  nome_paciente TEXT NOT NULL,
                                  data DATE NOT NULL,
                                  hora TIME NOT NULL, 
                                  convenio TEXT,
                                  tipo_consulta TEXT NOT NULL,
                                  emergencia INTEGER DEFAULT 0)''')
        self.conn.commit()

        self.cursor.execute("SELECT * FROM consultas LIMIT 1")
        columns = [description[0] for description in self.cursor.description]
        if 'nome_paciente' not in columns:
            self.cursor.execute("ALTER TABLE consultas ADD COLUMN nome_paciente TEXT")
            self.conn.commit()
            self.cursor.execute("UPDATE consultas SET nome_paciente = '' WHERE nome_paciente IS NULL")
            self.conn.commit()
            self.cursor.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(id) FROM consultas) WHERE name = 'consultas'")
            self.conn.commit()

        self.janela_principal()

    def obter_ultima_consulta(self, nome_paciente):
        self.cursor.execute("SELECT * FROM consultas WHERE nome_paciente = ? ORDER BY data DESC LIMIT 1",
                            (nome_paciente,))
        return self.cursor.fetchone()
    def programar_backup_diario(self):
        while True:
                # Obtém a data e hora atual
            agora = datetime.now()

                # Define o horário de backup para meia-noite
            horario_backup = agora.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

                # Calcula o tempo de espera até o horário de backup
            tempo_espera = (horario_backup - agora).total_seconds()

                # Aguarda até o horário de backup
            time.sleep(tempo_espera)

                # Realiza o backup diário
            self.backup_diario()

    def backup_diario(self):
            # Cria um diretório 'backups' se ainda não existir
        if not os.path.exists('documentos/backups'):
               os.makedirs('documentos/backups')

            # Obtém a data atual para nomear o arquivo de backup
               data_atual = datetime.now().strftime("%Y-%m-%d")
               nome_arquivo = f'backup_{data_atual}.db'

            # Copia o arquivo do banco de dados para a pasta de backups
               shutil.copyfile('clinica.db', f'documentos/backups/{nome_arquivo}')

        self.conn.commit()

    def cadastrar_paciente(self):
        CadastrarPacienteWindow(self)

    def paciente_cadastrado(self, nome_paciente):
        self.cursor.execute("SELECT * FROM pacientes WHERE nome = ?", (nome_paciente,))
        paciente = self.cursor.fetchone()
        return paciente is not None

    def agendar_consulta(self):
        AgendarConsultaWindow(self, self.conn, self.cursor)

    def visualizar_cadastro_paciente(self):
        VisualizarCadastroPacienteWindow(self)

    def gerar_planilha(self):
        # Consulta todos os pacientes e suas consultas (se houver)
        self.cursor.execute("""
            SELECT p.ID, p.Nome, p.Idade, p.Endereco, p.Telefone, p.CPF,
                   c.Data, c.Hora, c.Convenio, c.Tipo_Consulta, c.Emergencia
            FROM pacientes p
            LEFT JOIN consultas c ON p.Nome = c.Nome_Paciente
        """)
        pacientes_consultas = self.cursor.fetchall()

        # Cria um DataFrame pandas com os dados dos pacientes e suas consultas
        df_pacientes_consultas = pd.DataFrame(pacientes_consultas, columns=[
            "ID", "Nome", "Idade", "Endereço", "Telefone", "CPF",
            "Data Consulta", "Hora Consulta", "Convênio", "Tipo Consulta", "Emergência"
        ])

        # Mapeia o valor da coluna "Emergência" para "sim" quando for 1 (True) e "não" quando for 0 (False)
        df_pacientes_consultas["Emergência"] = df_pacientes_consultas["Emergência"].apply(
            lambda x: "sim" if x == 1 else ("não" if x == 0 else ""))

        # Salva o DataFrame como um arquivo CSV
        df_pacientes_consultas.to_csv("pacientes_consultas.csv", index=False)

        messagebox.showinfo("Sucesso", "Planilha gerada com sucesso! Arquivo 'pacientes_consultas.csv' criado.")
        os.startfile("pacientes_consultas.csv")

    def fechar_conexao(self):
        self.conn.close()
        sys.exit()

    def janela_principal(self):
        self.janela1 = tk.CTk()
        self.janela1.title("Clinica Bortolini")
        self.janela1.geometry("1020x780")

        # Adiciona widgets vazios para centralizar o conteúdo verticalmente
        for _ in range(5):
            tk.CTkLabel(self.janela1, text="", font=("Arial", 24)).pack()

        texto0 = tk.CTkLabel(self.janela1, text="Consultório Pediádrico Fabiana Bortolini", font=("Arial", 38, "bold"))
        texto0.pack(pady=20)

        texto1 = tk.CTkLabel(self.janela1, text="1. Cadastrar Paciente", font=("Arial", 24))
        texto1.pack(pady=10)

        botao1 = tk.CTkButton(self.janela1, text="✔", command=self.cadastrar_paciente, font=("Arial", 16))
        botao1.pack(pady=10)

        texto2 = tk.CTkLabel(self.janela1, text="2. Agendar Consulta", font=("Arial", 24))
        texto2.pack(pady=10)
        botao2 = tk.CTkButton(self.janela1, text="✔", command=self.agendar_consulta, font=("Arial", 16))
        botao2.pack(pady=10)

        texto3 = tk.CTkLabel(self.janela1, text="3. Visualizar Cadastro/Consulta", font=("Arial", 24))
        texto3.pack(pady=10)
        botao3 = tk.CTkButton(self.janela1, text="✔", command=self.visualizar_cadastro_paciente, font=("Arial", 16))
        botao3.pack(pady=10)

        texto4 = tk.CTkLabel(self.janela1, text="4. Gerar planilha", font=("Arial", 24))
        texto4.pack(pady=10)
        botao4 = tk.CTkButton(self.janela1, text="✔", command=self.gerar_planilha, font=("Arial", 16))
        botao4.pack(pady=10)

        texto5 = tk.CTkLabel(self.janela1, text="5. Sair", font=("Arial", 24))
        texto5.pack(pady=10)
        botao5 = tk.CTkButton(self.janela1, text="✔", command=self.fechar_conexao, font=("Arial", 16))
        botao5.pack()

        # Adiciona mais widgets vazios para centralizar o conteúdo verticalmente
        for _ in range(5):
            tk.CTkLabel(self.janela1, text="", font=("Arial", 24)).pack(pady=30)

        self.janela1.mainloop()


class CadastrarPacienteWindow(Toplevel):
    def __init__(self, clinica):
        super().__init__()
        self.title("Cadastrar Paciente")
        self.geometry("960x540")
        self.clinica = clinica

        self.nome_label = Label(self, text="Nome do paciente:", font=("Arial", 16))
        self.nome_label.pack()
        self.nome_entry = Entry(self, width=50, font=("Arial", 16))
        self.nome_entry.pack(pady=20)

        self.idade_label = Label(self, text="Idade do paciente:", font=("Arial", 16))
        self.idade_label.pack()
        self.idade_entry = Entry(self, width=5, font=("Arial", 16))
        self.idade_entry.pack(pady=20)

        self.endereco_label = Label(self, text="Endereço do paciente:", font=("Arial", 16))
        self.endereco_label.pack()
        self.endereco_entry = Entry(self, width=80, font=("Arial", 16))
        self.endereco_entry.pack(pady=20)

        self.telefone_label = Label(self, text="Telefone do paciente:", font=("Arial", 16))
        self.telefone_label.pack()
        self.telefone_entry = Entry(self, font=("Arial", 16))
        self.telefone_entry.pack(pady=20)

        self.CPF_label = Label(self, text="CPF do paciente:", font=("Arial", 16))
        self.CPF_label.pack()
        self.CPF_entry = Entry(self, font=("Arial", 16))
        self.CPF_entry.pack(pady=20)

        self.salvar_button = Button(self, text="Salvar", command=self.salvar_paciente)
        self.salvar_button.configure(bg='blue', fg='white', font=("Arial", 9), pady=10, width=10)
        self.salvar_button.pack(pady=15)

    def salvar_paciente(self):
        nome = self.nome_entry.get()
        idade = int(self.idade_entry.get())
        endereco = self.endereco_entry.get()
        telefone = self.telefone_entry.get()
        CPF = self.CPF_entry.get()

        # Verifica se já existe um paciente com os mesmos dados
        self.clinica.cursor.execute("SELECT * FROM pacientes WHERE CPF = ?",
                                    (CPF,))
        paciente_existente = self.clinica.cursor.fetchone()
        if paciente_existente:
            messagebox.showerror("Erro", "Já existe um paciente cadastrado com esses dados.")
            return

        # Insere o novo paciente caso não exista
        self.clinica.cursor.execute(
            "INSERT INTO pacientes (nome, idade, endereco, telefone, CPF) VALUES (?, ?, ?, ?, ?)",
            (nome, idade, endereco, telefone, CPF))
        self.clinica.conn.commit()
        messagebox.showinfo("Sucesso", "Paciente cadastrado com sucesso!")
        self.destroy()

class AgendarConsultaWindow(Toplevel):
    def __init__(self, clinica, conn, cursor):
        super().__init__()
        self.title("Agendar Consulta")
        self.geometry("960x540")
        self.clinica = clinica
        self.conn = conn
        self.cursor = cursor

        self.nome_paciente_label = Label(self, text="Nome do paciente:", font=("Arial", 16))
        self.nome_paciente_label.pack()
        self.nome_paciente_entry = Entry(self, width=50, font=("Arial", 16))
        self.nome_paciente_entry.pack(pady=20)

        self.data_label = Label(self, text="Data da consulta (DD/MM/AAAA):", font=("Arial", 16))
        self.data_label.pack()
        self.data_entry = Entry(self, width=10, font=("Arial", 16))
        self.data_entry.pack(pady=20)

        self.hora_label = Label(self, text="Hora da consulta (HH:MM):", font=("Arial", 16))
        self.hora_label.pack()
        self.hora_entry = Entry(self, width=5, font=("Arial", 16))
        self.hora_entry.pack(pady=20)

        self.convenio_label = Label(self, text="Convênio", font=("Arial", 16))
        self.convenio_label.pack()
        self.convenio_entry = Entry(self, font=("Arial", 16))
        self.convenio_entry.pack(pady=20)

        self.emergencia_var = IntVar()
        self.emergencia_checkbox = Checkbutton(self, text="Emergência", variable=self.emergencia_var, font=("Arial", 16))
        self.emergencia_checkbox.pack(pady=20)

        self.salvar_button = Button(self, text="Salvar", command=self.salvar_consulta)
        self.salvar_button.configure(bg='blue', fg='white', font=("Arial", 9), pady=10, width=10)
        self.salvar_button.pack(pady=15)

    def salvar_consulta(self):
        nome_paciente = self.nome_paciente_entry.get()

        # Verifica se o paciente está cadastrado
        if not self.clinica.paciente_cadastrado(nome_paciente):
            messagebox.showerror("Erro", "Paciente não encontrado. Cadastre o paciente antes de agendar a consulta.")
            return

        data = self.data_entry.get()
        hora = self.hora_entry.get()
        convenio = self.convenio_entry.get()
        emergencia = self.emergencia_var.get()


        # Verifica se a data está no formato correto
        try:
            nova_data = datetime.strptime(data, self.clinica.dateFormat).date()
        except ValueError:
            mensagem = f"Formato de data inválido. Use o formato {self.clinica.dateFormat} para a data."
            messagebox.showerror("Erro", mensagem)
            return
        if nova_data < datetime.today().date():
            messagebox.showerror("Erro", "Data de consulta não pode ser anterior à data atual.")
            return
        # Verifica se a hora está no formato correto
        try:
            nova_hora = datetime.strptime(hora, self.clinica.timeFormat).time()
        except ValueError:
            mensagem = f"Formato de hora inválido. Use o formato {self.clinica.timeFormat} para a hora."
            messagebox.showerror("Erro", mensagem)
            return

        # Converte a hora para um objeto datetime
        try:
            nova_hora = datetime.strptime(hora, self.clinica.timeFormat).time()
        except ValueError:
            messagebox.showerror("Erro", "Formato de hora inválido. Use o formato HH:MM para a hora.")
            return

        # Verificar se já existe uma consulta agendada para o mesmo dia e horário
        self.clinica.cursor.execute("SELECT * FROM consultas WHERE data = ? AND hora = ?", (str(data), str(hora)))
        consulta_existente = self.clinica.cursor.fetchone()

        if consulta_existente and not emergencia:
            messagebox.showerror("Erro", "Já existe uma consulta agendada para este dia e horário.")
            return

        # Converte a data e hora da nova consulta para um objeto datetime
        data_nova_consulta = datetime.strptime(data, self.clinica.dateFormat).date()
        hora_nova_consulta = datetime.strptime(hora, self.clinica.timeFormat).time()

        # Calcula os limites do intervalo de 30 minutos
        limite_inferior = (datetime.combine(data_nova_consulta, hora_nova_consulta) - timedelta(minutes=30)).time()
        limite_superior = (datetime.combine(data_nova_consulta, hora_nova_consulta) + timedelta(minutes=30)).time()
        # Converte os limites para strings no formato HH:MM
        limite_inferior_str = limite_inferior.strftime("%H:%M")
        limite_superior_str = limite_superior.strftime("%H:%M")

        # Verifica se existe alguma consulta dentro do intervalo de 30 minutos
        self.clinica.cursor.execute("SELECT * FROM consultas WHERE data = ? AND hora BETWEEN ? AND ?",
                                    (data, limite_inferior_str, limite_superior_str))

        consulta_proxima = self.clinica.cursor.fetchone()

        if consulta_proxima and not emergencia:
            messagebox.showerror("Erro", "Deve haver um intervalo mínimo de 30 minutos entre as consultas!")
            return
        # Verifica se é uma consulta de retorno
        ultima_consulta = self.obter_ultima_consulta(nome_paciente)
        if ultima_consulta:
            data_ultima_consulta = datetime.strptime(ultima_consulta[3], self.clinica.dateFormat)
            data_nova_consulta = datetime.strptime(data, self.clinica.dateFormat)
            diferenca_dias = (data_nova_consulta - data_ultima_consulta).days
            if diferenca_dias <= 15:
                tipo_consulta = "Consulta de Retorno"
                messagebox.showinfo("Tipo de Consulta", "Consulta agendada como Consulta de Retorno.")
            else:
                tipo_consulta = "Consulta Normal"
        else:
            tipo_consulta = "Primeira Consulta"

        # Insere a nova consulta
        self.clinica.cursor.execute(
            "INSERT INTO consultas (nome_paciente, data, hora, convenio, tipo_consulta, emergencia) VALUES (?, ?, ?, ?, ?, ?)",
            (nome_paciente, data, hora, convenio, tipo_consulta, emergencia))
        self.clinica.conn.commit()
        if emergencia:
            messagebox.showinfo("Sucesso", "Consulta de emergência agendada com sucesso!")
        else:
            messagebox.showinfo("Sucesso", "Consulta agendada com sucesso!")
        self.destroy()
    def obter_ultima_consulta(self, nome_paciente):
        self.clinica.cursor.execute("SELECT * FROM consultas WHERE nome_paciente = ? ORDER BY data DESC LIMIT 1",
                                    (nome_paciente,))
        return self.clinica.cursor.fetchone()

class VisualizarCadastroPacienteWindow(Toplevel):
    def __init__(self, clinica):
        super().__init__()
        self.title("Visualizar Cadastro/Consulta")
        self.geometry("780x600")
        self.clinica = clinica

        self.nome_paciente_label = Label(self, text="Nome ou CPF:", font=("Arial", 16))
        self.nome_paciente_label.pack()
        self.nome_paciente_entry = Entry(self, font=("Arial", 16))
        self.nome_paciente_entry.pack()

        self.confirmar_button = Button(self, text="Buscar", command=self.confirmar_nome_ou_CPF)
        self.confirmar_button.configure(bg='blue', fg='white', font=("Arial", 9))
        self.confirmar_button.pack(pady=15)

        self.dados_label = Label(self, text="Dados do paciente:", font=("Arial", 16))
        self.dados_label.pack()
        self.dados_text = Text(self, width=70, height=15, font=("Arial", 16))
        self.dados_text.pack()

    def confirmar_nome_ou_CPF(self):
        nome_ou_CPF = self.nome_paciente_entry.get()
        self.mostrar_dados_paciente(nome_ou_CPF)

    def mostrar_dados_paciente(self, nome_ou_CPF):
        self.dados_text.delete('1.0', END)
        self.clinica.cursor.execute("SELECT * FROM pacientes WHERE nome = ? OR CPF = ?", (nome_ou_CPF, nome_ou_CPF))
        paciente = self.clinica.cursor.fetchone()
        if paciente is not None:
            dados = f"Nome: {paciente[1]}\nIdade: {paciente[2]}\nEndereço: {paciente[3]}\nTelefone: {paciente[4]}\nCPF: {paciente[5]}\n"
            self.dados_text.insert(END, dados)

            self.clinica.cursor.execute("SELECT * FROM consultas WHERE nome_paciente = ?", (paciente[1],))
            consultas = self.clinica.cursor.fetchall()
            if consultas:
                dados_consultas = "\nConsultas Agendadas:\n"  # Inicializa a variável aqui
                for consulta in consultas:
                    tipo_consulta = consulta[5]
                    emergencia = consulta[6]
                    if emergencia:
                        tipo_consulta += " (Emergência)"
                    dados_consultas += f"Data: {consulta[3]}\tHora: {consulta[4]}\nConvênio: {consulta[1]}\nTipo: {tipo_consulta}\n\n"
                self.dados_text.insert(END, dados_consultas)
        else:
            messagebox.showerror("Erro", "Paciente não encontrado.")
        self.editar_button = Button(self, text="Editar Cadastro", command=self.editar_cadastro)
        self.editar_button.configure(bg='Indigo', fg='white', font=("Arial", 10, "bold"))
        self.editar_button.pack(pady=15)

        self.editar_consulta_button = Button(self, text="Editar Consulta", command=self.editar_consulta)
        self.editar_consulta_button.configure(bg='green', fg='white', font=("Arial", 10, "bold"))
        self.editar_consulta_button.pack(pady=15)

        self.cancelar_consulta_button = Button(self, text="Cancelar Consulta", command=self.cancelar_consulta)
        self.cancelar_consulta_button.configure(bg='red', fg='white', font=("Arial", 10, "bold"))
        self.cancelar_consulta_button.pack(pady=15)

    def editar_cadastro(self):
        nome_ou_CPF = self.nome_paciente_entry.get()
        self.editar_window = EditarCadastroPacienteWindow(self.clinica, nome_ou_CPF)
    def editar_consulta(self):
        nome_ou_CPF = self.nome_paciente_entry.get()
        ultima_consulta = self.clinica.obter_ultima_consulta(nome_ou_CPF)

        if ultima_consulta:
            consulta_id = ultima_consulta[0]
            self.editar_consulta_window = EditarConsultaWindow(self.clinica, consulta_id)
        else:
            messagebox.showerror("Erro", "Não foi possível encontrar uma consulta para editar.")

    def cancelar_consulta(self):
        nome_paciente = self.nome_paciente_entry.get()
        self.clinica.cursor.execute("""
            DELETE FROM consultas 
            WHERE id = (
                SELECT id 
                FROM consultas 
                WHERE nome_paciente = ? 
                ORDER BY data DESC 
                LIMIT 1
            )
        """, (nome_paciente,))
        self.clinica.conn.commit()
        messagebox.showinfo("Sucesso", "Consulta cancelada com sucesso!")
        self.destroy()

class EditarCadastroPacienteWindow(Toplevel):
    def __init__(self, clinica, nome_ou_CPF):
        super().__init__()
        self.title("Editar Cadastro de Paciente")
        self.geometry("960x540")
        self.clinica = clinica
        self.cursor = clinica.cursor

        self.nome_label = Label(self, text="Nome do paciente:", font=("Arial", 16))
        self.nome_label.pack()
        self.nome_entry = Entry(self, width=50, font=("Arial", 16))
        self.nome_entry.pack(pady=20)

        self.idade_label = Label(self, text="Idade do paciente:", font=("Arial", 16))
        self.idade_label.pack()
        self.idade_entry = Entry(self, width=5, font=("Arial", 16))
        self.idade_entry.pack(pady=20)

        self.endereco_label = Label(self, text="Endereço do paciente:", font=("Arial", 16))
        self.endereco_label.pack()
        self.endereco_entry = Entry(self, width=80, font=("Arial", 16))
        self.endereco_entry.pack(pady=20)

        self.telefone_label = Label(self, text="Telefone do paciente:", font=("Arial", 16))
        self.telefone_label.pack()
        self.telefone_entry = Entry(self, font=("Arial", 16))
        self.telefone_entry.pack(pady=20)

        self.CPF_label = Label(self, text="CPF do paciente:", font=("Arial", 16))
        self.CPF_label.pack()
        self.CPF_entry = Entry(self, font=("Arial", 16))
        self.CPF_entry.pack(pady=20)

        # Preenche os campos com os dados do paciente selecionado
        self.preencher_dados(nome_ou_CPF)

        self.salvar_button = Button(self, text="Salvar", command=self.salvar_edicao)
        self.salvar_button.configure(bg='blue', fg='white', font=("Arial", 9), pady=10, width=10)
        self.salvar_button.pack(pady=15)

    def preencher_dados(self, nome_ou_CPF):
        self.clinica.cursor.execute("SELECT * FROM pacientes WHERE nome = ? OR CPF = ?", (nome_ou_CPF, nome_ou_CPF))
        paciente = self.clinica.cursor.fetchone()
        if paciente is not None:
            self.nome_entry.insert(0, paciente[1])
            self.idade_entry.insert(0, paciente[2])
            self.endereco_entry.insert(0, paciente[3])
            self.telefone_entry.insert(0, paciente[4])
            self.CPF_entry.insert(0, paciente[5])

    def salvar_edicao(self):
        # Obtém os novos dados do paciente
        nome = self.nome_entry.get()
        idade = int(self.idade_entry.get())
        endereco = self.endereco_entry.get()
        telefone = self.telefone_entry.get()
        CPF = self.CPF_entry.get()

        # Atualiza os dados na base de dados
        self.clinica.cursor.execute(
            "UPDATE pacientes SET nome = ?, idade = ?, endereco = ?, telefone = ? WHERE CPF = ?",
            (nome, idade, endereco, telefone, CPF))
        self.clinica.conn.commit()
        messagebox.showinfo("Sucesso", "Cadastro do paciente atualizado com sucesso!")
        self.destroy()

class EditarConsultaWindow(Toplevel):
    def __init__(self, clinica, consulta_id):
        super().__init__()
        self.title("Editar Consulta")
        self.geometry("960x540")
        self.clinica = clinica
        self.consulta_id = consulta_id

        self.data_label = Label(self, text="Nova data da consulta (DD/MM/AAAA):", font=("Arial", 16))
        self.data_label.pack()
        self.data_entry = Entry(self, width=10, font=("Arial", 16))
        self.data_entry.pack(pady=20)

        self.hora_label = Label(self, text="Nova hora da consulta (HH:MM):", font=("Arial", 16))
        self.hora_label.pack()
        self.hora_entry = Entry(self, width=5, font=("Arial", 16))
        self.hora_entry.pack(pady=20)

        self.convenio_label = Label(self, text="Convênio", font=("Arial", 16))
        self.convenio_label.pack()
        self.convenio_entry = Entry(self, font=("Arial", 16))
        self.convenio_entry.pack(pady=20)

        self.emergencia_var = IntVar()
        self.emergencia_checkbox = Checkbutton(self, text="Emergência", variable=self.emergencia_var, font=("Arial", 16))
        self.emergencia_checkbox.pack(pady=20)

        self.salvar_button = Button(self, text="Salvar", command=self.salvar_consulta)
        self.salvar_button.configure(bg='blue', fg='white', font=("Arial", 9), pady=10, width=10)
        self.salvar_button.pack(pady=15)

    def salvar_consulta(self):
        nova_data = self.data_entry.get()
        nova_hora = self.hora_entry.get()
        convenio = self.convenio_entry.get()
        emergencia = self.emergencia_var.get()

        # Verifica se a data está no formato correto
        try:
            nova_data_dt = datetime.strptime(nova_data, self.clinica.dateFormat).date()
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use o formato DD/MM/AAAA.")
            return

        # Verifica se a hora está no formato correto
        try:
            nova_hora_dt = datetime.strptime(nova_hora, self.clinica.timeFormat).time()
        except ValueError:
            messagebox.showerror("Erro", "Formato de hora inválido. Use o formato HH:MM.")
            return

        # Verifica se a nova consulta está dentro do horário comercial, se necessário

        # Converte a data e hora da nova consulta para um objeto datetime
        nova_consulta_dt = datetime.combine(nova_data_dt, nova_hora_dt)

        # Verifica se a nova consulta está dentro do horário comercial, se necessário

        # Atualiza a consulta no banco de dados
        self.clinica.cursor.execute("""
            UPDATE consultas 
            SET data = ?, hora = ?, convenio = ?, emergencia = ?
            WHERE id = ?
        """, (nova_data, nova_hora, convenio, emergencia, self.consulta_id))
        self.clinica.conn.commit()

        messagebox.showinfo("Sucesso", "Consulta atualizada com sucesso!")
        self.destroy()

class CancelarConsultaWindow(Toplevel):
    def __init__(self, clinica, nome_paciente):
        super().__init__()
        self.title("Cancelar Consulta")
        self.geometry("960x540")
        self.clinica = clinica
        self.nome_paciente = nome_paciente

        self.consulta_label = Label(self, text="Consulta a ser cancelada:", font=("Arial", 16))
        self.consulta_label.pack()
        self.consulta_text = Text(self, width=70, height=10, font=("Arial", 16))
        self.consulta_text.pack()

        self.confirmar_button = Button(self, text="Cancelar Consulta", command=self.cancelar_consulta)
        self.confirmar_button.configure(bg='red', fg='white', font=("Arial", 9))
        self.confirmar_button.pack(pady=15)

        self.mostrar_consulta()

    def mostrar_consulta(self):
        self.clinica.cursor.execute("SELECT * FROM consultas WHERE nome_paciente = ? ORDER BY data DESC LIMIT 1",
                                    (self.nome_paciente,))
        consulta = self.clinica.cursor.fetchone()
        if consulta is not None:
            emergencia = "sim" if consulta[6] == 1 else "não"
            dados_consulta = f"Data: {consulta[3]}\nHora: {consulta[4]}\nConvênio: {consulta[1]}\nTipo: {consulta[5]}\nEmergência: {emergencia}"
            self.consulta_text.insert(END, dados_consulta)
        else:
            messagebox.showerror("Erro", "Não foi possível encontrar uma consulta para cancelar.")

    def cancelar_consulta(self):
        self.clinica.cursor.execute("DELETE FROM consultas WHERE nome_paciente = ? ORDER BY data DESC LIMIT 1",
                                    (self.nome_paciente,))
        self.clinica.conn.commit()
        messagebox.showinfo("Sucesso", "Consulta cancelada com sucesso!")
        self.destroy()


clinica = ClinicaPediatrica()



