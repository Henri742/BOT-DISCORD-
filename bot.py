import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import os
import sqlite3
import json
import datetime
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 🗄️ INICIALIZAÇÃO E BANCO DE DADOS
# ==========================================
# Carrega os textos e questões do ficheiro JSON
try:
    with open('conteudo.json', 'r', encoding='utf-8') as f:
        DADOS = json.load(f)
except FileNotFoundError:
    print("ERRO: Ficheiro conteudo.json não encontrado. Certifique-se de que o criou na mesma pasta.")
    DADOS = {"resumos": {}, "questoes": {}}

def iniciar_banco():
    # Verifica se a pasta existe no sistema do Railway
    if not os.path.exists('/data'):
        os.makedirs('/data')
        
    conn = sqlite3.connect('/data/alunos.db') # Note a barra antes do data
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alunos (user_id TEXT PRIMARY KEY, xp INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS questoes_resolvidas (user_id TEXT, materia TEXT, questao TEXT, UNIQUE(user_id, materia, questao))''')
    conn.commit()
    conn.close()

def adicionar_xp(user_id, pontos):
    conn = sqlite3.connect('/data/alunos.db')
    c = conn.cursor()
    c.execute('''INSERT INTO alunos (user_id, xp) VALUES (?, ?) 
                 ON CONFLICT(user_id) DO UPDATE SET xp = xp + ?''', (str(user_id), pontos, pontos))
    conn.commit()
    conn.close()

def pegar_xp(user_id):
    conn = sqlite3.connect('/data/alunos.db')
    c = conn.cursor()
    c.execute('SELECT xp FROM alunos WHERE user_id = ?', (str(user_id),))
    res = c.fetchone()
    conn.close()
    return res[0] if res else 0

# --- NOVAS FUNÇÕES DO HISTÓRICO ---
def registrar_questao(user_id, materia, questao_texto):
    conn = sqlite3.connect('alunos.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO questoes_resolvidas VALUES (?, ?, ?)', (str(user_id), materia, questao_texto))
    conn.commit()
    conn.close()

def pegar_resolvidas(user_id, materia):
    conn = sqlite3.connect('alunos.db')
    c = conn.cursor()
    c.execute('SELECT questao FROM questoes_resolvidas WHERE user_id = ? AND materia = ?', (str(user_id), materia))
    res = {linha[0] for linha in c.fetchall()} # Retorna um Set (conjunto) com os textos das questões
    conn.close()
    return res

def resetar_resolvidas(user_id, materia):
    conn = sqlite3.connect('alunos.db')
    c = conn.cursor()
    c.execute('DELETE FROM questoes_resolvidas WHERE user_id = ? AND materia = ?', (str(user_id), materia))
    conn.commit()
    conn.close()

class GustavoLMS(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # <-- Esta é a linha que remove o aviso
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        iniciar_banco()
        await self.tree.sync()
        print(f"[{datetime.datetime.now()}] 🟢 SISTEMA LMS MODULAR E BANCO DE DADOS ONLINE.")

bot = GustavoLMS()

# ==========================================
# 🖥️ COMPONENTES VISUAIS (HUB E SIMULADO)
# ==========================================
class DropdownResumos(discord.ui.Select):
    def __init__(self, curso):
        self.curso = curso
        if curso in DADOS["resumos"]:
            opcoes = [discord.SelectOption(label=k) for k in DADOS["resumos"][curso].keys()]
        else:
            opcoes = [discord.SelectOption(label="Sem conteúdo")]
        super().__init__(placeholder="Selecione a aula para ler o resumo...", options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        texto = DADOS["resumos"][self.curso].get(self.values[0], "Conteúdo não encontrado.")
        embed = discord.Embed(title=f"📖 {self.values[0]}", description=texto, color=0x3498db)
        await interaction.response.edit_message(embed=embed)

class PainelCursos(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="Matemática Aplicada", style=discord.ButtonStyle.primary, emoji="🔢", row=0)
    async def btn_ma(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos de Matemática Aplicada:", view=discord.ui.View().add_item(DropdownResumos("MA")), ephemeral=True)
        
    @discord.ui.button(label="Gestão de Times", style=discord.ButtonStyle.success, emoji="👥", row=0)
    async def btn_gt(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos de Gestão de Times:", view=discord.ui.View().add_item(DropdownResumos("GT")), ephemeral=True)

    @discord.ui.button(label="Lógica Matemática", style=discord.ButtonStyle.secondary, emoji="⚖️", row=1)
    async def btn_ml(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos de Lógica Matemática:", view=discord.ui.View().add_item(DropdownResumos("Matematica_Logica")), ephemeral=True)
        
    @discord.ui.button(label="Lógica Programação", style=discord.ButtonStyle.danger, emoji="💻", row=1)
    async def btn_lp(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos de Lógica de Programação:", view=discord.ui.View().add_item(DropdownResumos("Programacao")), ephemeral=True)

class ViewSimulado(discord.ui.View):
    def __init__(self, user_id, questoes, materia): # <-- Adicionamos a matéria aqui
        super().__init__(timeout=600)
        self.user_id = user_id
        self.questoes = questoes
        self.materia = materia
        self.total = len(questoes)
        self.atual = 0
        self.pontos = 0

    async def atualizar(self, interaction: discord.Interaction):
        if self.atual >= self.total:
            xp_ganho = self.pontos * 20
            adicionar_xp(self.user_id, xp_ganho)
            embed = discord.Embed(title="🎓 Boletim do Simulado", description=f"**Acertos:** {self.pontos}/{self.total}\n⭐ **XP Salvo:** +{xp_ganho}", color=0x2ecc71)
            await interaction.response.edit_message(embed=embed, view=None)
            return

        q = self.questoes[self.atual]
        # Salva a questão no banco de dados para não repetir mais!
        registrar_questao(self.user_id, self.materia, q['q'])
        
        embed = discord.Embed(title=f"Questão {self.atual + 1} / {self.total}", description=f"**{q['q']}**", color=0xe67e22)
        self.clear_items()
        
        letras = ["A", "B", "C", "D"]
        for idx, opt in enumerate(q['opts']):
            btn = discord.ui.Button(label=f"{letras[idx]}) {opt}"[:80], custom_id=str(idx), style=discord.ButtonStyle.secondary)
            async def callback(inter: discord.Interaction, button=btn):
                if inter.user.id != self.user_id: return await inter.response.send_message("Inicie o seu próprio simulado!", ephemeral=True)
                if int(button.custom_id) == self.questoes[self.atual]['ans']: self.pontos += 1
                self.atual += 1
                await self.atualizar(inter)
            btn.callback = callback
            self.add_item(btn)

        if interaction.response.is_done(): await interaction.edit_original_response(embed=embed, view=self)
        else: await interaction.response.edit_message(embed=embed, view=self)

# ==========================================
# 🧩 JOGO TABELA-VERDADE (MINI-GAME)
# ==========================================
class ModalTabelaVerdade(discord.ui.Modal):
    l1 = discord.ui.TextInput(label='1. Quando p=V, q=V', max_length=1, placeholder="V ou F")
    l2 = discord.ui.TextInput(label='2. Quando p=V, q=F', max_length=1, placeholder="V ou F")
    l3 = discord.ui.TextInput(label='3. Quando p=F, q=V', max_length=1, placeholder="V ou F")
    l4 = discord.ui.TextInput(label='4. Quando p=F, q=F', max_length=1, placeholder="V ou F")

    def __init__(self, titulo, exp, resp_certa):
        # O título do Modal agora mostra a operação exata
        super().__init__(title=titulo[:45])
        self.exp = exp
        self.resp_certa = resp_certa

    async def on_submit(self, interaction: discord.Interaction):
        resp_user = [self.l1.value.upper(), self.l2.value.upper(), self.l3.value.upper(), self.l4.value.upper()]
        if resp_user == self.resp_certa:
            adicionar_xp(interaction.user.id, 30)
            await interaction.response.send_message(f"✅ Correto! Você resolveu **{self.exp}** e ganhou 30 XP.")
        else:
            await interaction.response.send_message(f"❌ Errou! O gabarito de **{self.exp}** era: {', '.join(self.resp_certa)}\nVocê digitou: {', '.join(resp_user)}", ephemeral=True)



# ==========================================
# 🚀 COMANDOS DO BOT (SLASH COMMANDS)
# ==========================================

class ViewPainelSimulado(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Fica ativo para sempre

    @discord.ui.button(label="Iniciar Novo Simulado", style=discord.ButtonStyle.primary, emoji="📝", custom_id="persistent:iniciar")
    async def iniciar_sala(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Criar categoria ou canal privado
        guild = interaction.guild
        user = interaction.user
        
        # Configura as permissões: Ninguém vê, exceto o bot e o aluno
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        nome_canal = f"simulado-{user.name}".lower()
        canal_privado = await guild.create_text_channel(nome_canal, overwrites=overwrites)
        
        await interaction.response.send_message(f"✅ Sua sala de prova foi criada: {canal_privado.mention}", ephemeral=True)
        
        # 2. Enviar mensagem inicial no canal novo para escolher a matéria
        embed = discord.Embed(title="🎒 Bem-vindo à Sala de Prova", description="Escolha a matéria para começar:", color=0x8e44ad)
        await canal_privado.send(embed=embed, view=PainelCursos())

@bot.tree.command(name="setup_simulado", description="Cria o botão fixo para abrir salas de simulado.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_simulado(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📝 Central de Simulados", 
        description="Clique no botão abaixo para abrir uma sala privada e iniciar sua prova.\n\n*O canal será deletado automaticamente ao fim do teste.*", 
        color=0x3498db
    )
    await interaction.response.send_message("Painel criado!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=ViewPainelSimulado())

@bot.tree.command(name="helpprof", description="Manual completo de todas as funções da plataforma.")
async def helpprof(interaction: discord.Interaction):
    embed = discord.Embed(title="📚 Manual do Gustavo LMS", description="As funcionalidades disponíveis no servidor:", color=0xf1c40f)
    embed.add_field(name="`/hub`", value="Abre o painel central com os resumos de todas as disciplinas.", inline=False)
    embed.add_field(name="`/simulado`", value="Inicia um teste real de múltipla escolha valendo XP.", inline=False)
    embed.add_field(name="`/helpaluno`", value="Marque todos os colegas para ajudarem com uma dúvida sua.", inline=False)
    embed.add_field(name="`/calcular`", value="Calculadora instantânea (+, -, *, /, %).", inline=False)
    embed.add_field(name="`/tabela_verdade`", value="Treine preenchendo os valores de uma tabela-verdade.", inline=False)
    embed.add_field(name="`/pomodoro`", value="Timer de foco personalizado em minutos.", inline=False)
    embed.add_field(name="`/status` e `/ranking`", value="Veja o seu nível ou os melhores alunos do servidor.", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="helpaluno", description="Publique uma dúvida e chame a atenção da turma!")
@app_commands.describe(duvida="Descreva a sua dúvida de forma clara")
async def helpaluno(interaction: discord.Interaction, duvida: str):
    embed = discord.Embed(title="🚨 Pedido de Ajuda!", description=f"**Dúvida:**\n{duvida}", color=0xe74c3c)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None)
    embed.set_footer(text="Colegas, respondam abaixo se souberem a solução!")
    await interaction.response.send_message(content="@here Temos um colega a precisar de ajuda!", embed=embed)

@bot.tree.command(name="hub", description="Acessa todos os resumos e conteúdos das disciplinas.")
async def hub(interaction: discord.Interaction):
    embed = discord.Embed(title="🏛️ Campus Virtual Gustavo", description="Selecione a sua disciplina abaixo para iniciar os estudos:", color=0x8e44ad)
    await interaction.response.send_message(embed=embed, view=PainelCursos())

@bot.tree.command(name="simulado", description="Inicia um teste real valendo XP permanente.")
@app_commands.choices(
    materia=[
        app_commands.Choice(name="Matemática Aplicada", value="Matematica_Aplicada"), 
        app_commands.Choice(name="Gestão de Times", value="Gestao_Times"),
        app_commands.Choice(name="Lógica Matemática", value="Matematica_Logica"),
        app_commands.Choice(name="Lógica de Programação", value="Programacao")
    ],
    quantidade=[app_commands.Choice(name=str(i), value=i) for i in [2, 5, 10, 15, 20, 25, 30]]
)
async def simulado(interaction: discord.Interaction, materia: str, quantidade: int):
    banco_completo = DADOS["questoes"].get(materia, [])
    if not banco_completo:
        return await interaction.response.send_message("❌ Ainda não há questões para esta matéria.", ephemeral=True)
        
    # Pega as questões que o aluno já fez
    resolvidas = pegar_resolvidas(interaction.user.id, materia)
    # Filtra: Cria uma lista só com as questões INÉDITAS
    banco_disponivel = [q for q in banco_completo if q['q'] not in resolvidas]

    # Se o aluno já respondeu todas as questões dessa matéria
    if not banco_disponivel:
        resetar_resolvidas(interaction.user.id, materia)
        banco_disponivel = banco_completo
        await interaction.channel.send(f"🔄 Parabéns, {interaction.user.mention}! Você já havia resolvido todas as questões de **{materia}**. O seu histórico desta disciplina foi zerado para continuar treinando.")

    qtd_real = min(quantidade, len(banco_disponivel))
    sorteadas = random.sample(banco_disponivel, qtd_real)
    
    view = ViewSimulado(interaction.user.id, sorteadas, materia)
    embed = discord.Embed(title="📝 Prova Iniciada (Apenas Inéditas)", description=f"Disciplina: **{materia}**\nQuestões: **{qtd_real}**\nBoa sorte!", color=0xf1c40f)
    await interaction.response.send_message(embed=embed)
    await view.atualizar(interaction)

@bot.tree.command(name="calcular", description="Calculadora rápida e funcional (+, -, *, /, %).")
@app_commands.choices(operacao=[
    app_commands.Choice(name="Somar (+)", value="+"), 
    app_commands.Choice(name="Subtrair (-)", value="-"), 
    app_commands.Choice(name="Multiplicar (*)", value="*"), 
    app_commands.Choice(name="Dividir (/)", value="/"), 
    app_commands.Choice(name="Resto (%)", value="%")
])
async def calcular(interaction: discord.Interaction, n1: float, operacao: str, n2: float):
    try:
        res = eval(f"{n1} {operacao} {n2}")
        embed = discord.Embed(title="🧮 Calculadora", description=f"**Cálculo:** {n1} {operacao} {n2}\n**Resultado:** `{res}`", color=0x3498db)
        await interaction.response.send_message(embed=embed)
    except ZeroDivisionError:
        await interaction.response.send_message("❌ Erro: É impossível dividir por zero!", ephemeral=True)

# ==========================================
# (Procure o comando /tabela_verdade lá embaixo e substitua por este:)
# ==========================================
@bot.tree.command(name="tabela_verdade", description="Treine o preenchimento dos valores da tabela-verdade.")
async def tabela_verdade(interaction: discord.Interaction):
    desafios = [
        # Conjunção (E / ^)
        {"titulo": "Conjunção: p ^ q", "exp": "p ^ q", "resp": ["V", "F", "F", "F"]},
        {"titulo": "Conjunção: ~p ^ q", "exp": "~p ^ q", "resp": ["F", "F", "V", "F"]},
        {"titulo": "Conjunção: p ^ ~q", "exp": "p ^ ~q", "resp": ["F", "V", "F", "F"]},
        
        # Disjunção (OU / v)
        {"titulo": "Disjunção: p v q", "exp": "p v q", "resp": ["V", "V", "V", "F"]},
        {"titulo": "Disjunção: ~p v q", "exp": "~p v q", "resp": ["V", "F", "V", "V"]},
        {"titulo": "Disjunção: p v ~q", "exp": "p v ~q", "resp": ["V", "V", "F", "V"]},
        
        # Condicional (Se... então / ->)
        {"titulo": "Condicional: p -> q", "exp": "p -> q", "resp": ["V", "F", "V", "V"]},
        {"titulo": "Condicional: ~p -> q", "exp": "~p -> q", "resp": ["V", "V", "V", "F"]},
        {"titulo": "Condicional: p -> ~q", "exp": "p -> ~q", "resp": ["F", "V", "V", "V"]},
        
        # Bicondicional (Se e somente se / <->)
        {"titulo": "Bicondicional: p <-> q", "exp": "p <-> q", "resp": ["V", "F", "F", "V"]},
        {"titulo": "Bicondicional: ~p <-> q", "exp": "~p <-> q", "resp": ["F", "V", "V", "F"]},
        {"titulo": "Bicondicional: p <-> ~q", "exp": "p <-> ~q", "resp": ["F", "V", "V", "F"]}
    ]
    escolhido = random.choice(desafios)
    await interaction.response.send_modal(ModalTabelaVerdade(escolhido["titulo"], escolhido["exp"], escolhido["resp"]))


@bot.tree.command(name="pomodoro", description="Timer de foco personalizado para os seus estudos.")
async def pomodoro(interaction: discord.Interaction, minutos: int):
    if minutos <= 0 or minutos > 120:
        return await interaction.response.send_message("❌ Escolha um tempo entre 1 e 120 minutos.", ephemeral=True)
    await interaction.response.send_message(f"🍅 **Foco Ativado!** {interaction.user.mention}, estude sem distrações por **{minutos} minutos**.")
    await asyncio.sleep(minutos * 60)
    await interaction.followup.send(f"⏰ {interaction.user.mention}, o seu tempo de {minutos} minutos acabou! Faça uma merecida pausa.")

@bot.tree.command(name="status", description="Veja o seu XP salvo de forma permanente.")
async def status(interaction: discord.Interaction):
    xp = pegar_xp(interaction.user.id)
    embed = discord.Embed(title="📊 Status Académico", color=0x2c3e50)
    embed.add_field(name="Aluno", value=interaction.user.mention, inline=False)
    embed.add_field(name="Nível Atual", value=f"✨ Lvl {xp//100}", inline=True)
    embed.add_field(name="XP Total", value=f"⭐ {xp} XP", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ranking", description="Veja o Quadro de Honra com os melhores alunos.")
async def ranking(interaction: discord.Interaction):
    conn = sqlite3.connect('alunos.db')
    c = conn.cursor()
    c.execute('SELECT user_id, xp FROM alunos ORDER BY xp DESC LIMIT 5')
    top5 = c.fetchall()
    conn.close()

    embed = discord.Embed(title="🏆 Quadro de Honra (Top 5)", description="Os alunos com mais pontos de experiência:", color=0xf1c40f)
    if not top5:
        embed.description = "Ainda não há alunos com XP no sistema."
    else:
        for i, (uid, xp) in enumerate(top5):
            embed.add_field(name=f"{i+1}º Lugar", value=f"<@{uid}> - **{xp} XP**", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="limpar_chat", description="Deleta as mensagens do canal (Apenas Admins).")
@app_commands.checks.has_permissions(manage_messages=True)
async def limpar_chat(interaction: discord.Interaction, quantidade: int):
    await interaction.response.defer(ephemeral=True)
    apagadas = await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f"🧹 Chat limpo. {len(apagadas)} mensagens eliminadas.", ephemeral=True)

@bot.tree.command(name="backup", description="Baixa o arquivo do banco de dados (Apenas Admins).")
@app_commands.checks.has_permissions(administrator=True) # Só você e outros admins podem usar
async def backup(interaction: discord.Interaction):
    try:
        # Envia o arquivo alunos.db direto no chat, visível só para você (ephemeral)
        await interaction.response.send_message("📦 Aqui está o backup mais recente do banco de dados:", file=discord.File('alunos.db'), ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao gerar backup: {e}", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))