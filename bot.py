import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import os
import sqlite3
import json
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 🗄️ BANCO DE DADOS (VOLUME /data)
# ==========================================
DB_PATH = '/data/alunos.db'

def iniciar_banco():
    if not os.path.exists('/data'):
        try: os.makedirs('/data')
        except: pass
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alunos (user_id TEXT PRIMARY KEY, xp INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS questoes_resolvidas (user_id TEXT, materia TEXT, questao TEXT, UNIQUE(user_id, materia, questao))''')
    conn.commit()
    conn.close()

def adicionar_xp(user_id, pontos):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('INSERT INTO alunos (user_id, xp) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET xp = xp + ?', (str(user_id), pontos, pontos))
    conn.commit(); conn.close()

def pegar_xp(user_id):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('SELECT xp FROM alunos WHERE user_id = ?', (str(user_id),)); res = c.fetchone(); conn.close()
    return res[0] if res else 0

def registrar_questao(user_id, materia, questao_texto):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO questoes_resolvidas VALUES (?, ?, ?)', (str(user_id), materia, questao_texto))
    conn.commit(); conn.close()

def pegar_resolvidas(user_id, materia):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('SELECT questao FROM questoes_resolvidas WHERE user_id = ? AND materia = ?', (str(user_id), materia))
    res = {linha[0] for linha in c.fetchall()}; conn.close()
    return res

# ==========================================
# 🖥️ COMPONENTES VISUAIS (SIMULADO E HUB)
# ==========================================

try:
    with open('conteudo.json', 'r', encoding='utf-8') as f:
        DADOS = json.load(f)
except:
    DADOS = {"resumos": {}, "questoes": {}}

class DropdownResumos(discord.ui.Select):
    def __init__(self, curso):
        self.curso = curso
        nomes = {
            "MA": "Matemática Aplicada", 
            "GT": "Gestão de Times", 
            "Matematica_Logica": "Lógica Matemática", 
            "Programacao": "Lógica de Programação"
        }
        opcoes = [discord.SelectOption(label=k) for k in DADOS["resumos"].get(curso, {}).keys()] or [discord.SelectOption(label="Vazio")]
        super().__init__(placeholder=f"Resumos de {nomes.get(curso, curso)}...", options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        texto = DADOS["resumos"][self.curso].get(self.values[0], "Conteúdo não encontrado.")
        await interaction.response.edit_message(embed=discord.Embed(title=f"📖 {self.values[0]}", description=texto, color=0x3498db))

class PainelCursos(discord.ui.View):
    def __init__(self): 
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Matemática Aplicada", style=discord.ButtonStyle.primary, emoji="🔢")
    async def btn_ma(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos de Matemática Aplicada:", view=discord.ui.View().add_item(DropdownResumos("MA")), ephemeral=True)

    @discord.ui.button(label="Gestão de Times", style=discord.ButtonStyle.success, emoji="👥")
    async def btn_gt(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos de Gestão de Times:", view=discord.ui.View().add_item(DropdownResumos("GT")), ephemeral=True)

    @discord.ui.button(label="Lógica Matemática", style=discord.ButtonStyle.secondary, emoji="⚖️")
    async def btn_ml(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos de Lógica Matemática:", view=discord.ui.View().add_item(DropdownResumos("Matematica_Logica")), ephemeral=True)

    @discord.ui.button(label="Lógica de Programação", style=discord.ButtonStyle.danger, emoji="💻")
    async def btn_lp(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos de Lógica de Programação:", view=discord.ui.View().add_item(DropdownResumos("Programacao")), ephemeral=True)
class ViewSimulado(discord.ui.View):
    def __init__(self, user_id, questoes, materia):
        super().__init__(timeout=600)
        self.user_id, self.questoes, self.materia = user_id, questoes, materia
        self.total, self.atual, self.pontos = len(questoes), 0, 0

    async def atualizar(self, interaction: discord.Interaction):
        if self.atual >= self.total:
            xp = self.pontos * 20
            adicionar_xp(self.user_id, xp)
            embed = discord.Embed(title="📊 Simulado Finalizado", description=f"✅ Acertos: {self.pontos}/{self.total}\n⭐ XP: +{xp}", color=0x2ecc71)
            await interaction.response.edit_message(content="🏁 Prova encerrada! O canal fechará em 15s.", embed=None, view=None)
            await interaction.channel.send(embed=embed)
            await asyncio.sleep(15); await interaction.channel.delete(); return

        q = self.questoes[self.atual]
        registrar_questao(self.user_id, self.materia, q['q'])
        embed = discord.Embed(title=f"Questão {self.atual+1}/{self.total}", description=f"**{q['q']}**", color=0xe67e22)
        self.clear_items()
        for idx, opt in enumerate(q['opts']):
            btn = discord.ui.Button(label=f"{chr(65+idx)}) {opt}"[:80], custom_id=str(idx), style=discord.ButtonStyle.secondary)
            async def cb(inter, b=btn):
                if inter.user.id != self.user_id: return
                if int(b.custom_id) == self.questoes[self.atual]['ans']: self.pontos += 1
                self.atual += 1; await self.atualizar(inter)
            btn.callback = cb; self.add_item(btn)
        if interaction.response.is_done(): await interaction.edit_original_response(embed=embed, view=self)
        else: await interaction.response.edit_message(embed=embed, view=self)

class ViewEscolhaSimulado(discord.ui.View):
    def __init__(self, user_id): 
        super().__init__(timeout=None)
        self.user_id = user_id
    
    @discord.ui.select(placeholder="Escolha a matéria para a prova...", options=[
        discord.SelectOption(label="Matemática Aplicada", value="Matematica_Aplicada", emoji="🔢"),
        discord.SelectOption(label="Gestão de Times", vvalue="Gestao_Times", emoji="👥"),
        discord.SelectOption(label="Lógica Matemática", value="Matematica_Logica", emoji="⚖️"),
        discord.SelectOption(label="Lógica de Programação", value="Programacao", emoji="💻")
    ])
    async def select_materia(self, interaction: discord.Interaction, select: discord.ui.Select):
        materia_id = select.values[0]
        todas = DADOS["questoes"].get(materia_id, [])
        
        # LOG PARA TESTE (Aparecerá no Railway)
        print(f"DEBUG: Matéria selecionada: {materia_id} | Total no JSON: {len(todas)}")
        
        resolvidas = pegar_resolvidas(self.user_id, materia_id)
        disponiveis = [q for q in todas if q['q'] not in resolvidas]
        
        if not disponiveis:
            # Se não há disponíveis, mas existem questões no JSON, o problema é o banco
            if todas:
                return await interaction.response.send_message(f"❌ Você já acertou as {len(todas)} questões de {materia_id} que existem no sistema!", ephemeral=True)
            else:
                return await interaction.response.send_message(f"⚠️ O arquivo conteudo.json está vazio para a chave: {materia_id}", ephemeral=True)
        
        random.shuffle(disponiveis)
        view = ViewSimulado(self.user_id, disponiveis[:5], materia_id)
        await interaction.response.edit_message(content=f"📝 Iniciando Simulado de {materia_id}...", view=None)
        await view.atualizar(interaction)
class ViewPainelSimulado(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Iniciar Novo Simulado", style=discord.ButtonStyle.primary, emoji="📝", custom_id="persistent:iniciar")
    async def iniciar_sala(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True), interaction.guild.me: discord.PermissionOverwrite(read_messages=True)}
        canal = await interaction.guild.create_text_channel(f"prova-{interaction.user.name}".lower(), overwrites=overwrites)
        await interaction.response.send_message(f"✅ Sala privada criada: {canal.mention}", ephemeral=True)
        await canal.send(embed=discord.Embed(title="📚 Preparado para o Simulado?", description="Escolha a matéria abaixo para começar imediatamente.", color=0x8e44ad), view=ViewEscolhaSimulado(interaction.user.id))

class ModalTabelaVerdade(discord.ui.Modal):
    l1 = discord.ui.TextInput(label='1. p=V, q=V', max_length=1, placeholder="V ou F")
    l2 = discord.ui.TextInput(label='2. p=V, q=F', max_length=1, placeholder="V ou F")
    l3 = discord.ui.TextInput(label='3. p=F, q=V', max_length=1, placeholder="V ou F")
    l4 = discord.ui.TextInput(label='4. p=F, q=F', max_length=1, placeholder="V ou F")
    
    def __init__(self, t, e, r): super().__init__(title=t[:45]); self.exp, self.resp = e, r
    
    async def on_submit(self, interaction: discord.Interaction):
        u = [self.l1.value.upper(), self.l2.value.upper(), self.l3.value.upper(), self.l4.value.upper()]
        status = "✅ ACERTOU!" if u == self.resp else "❌ ERROU!"
        if u == self.resp: adicionar_xp(interaction.user.id, 30)
        
        res_formatada = f"Sua resposta: `{' '.join(u)}` | Gabarito: `{' '.join(self.resp)}`"
        await interaction.response.send_message(f"**{status}**\nExpressão: `{self.exp}`\n{res_formatada}")

# ==========================================
# 🚀 CORE DO BOT
# ==========================================

class GustavoLMS(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self):
        iniciar_banco()
        self.add_view(ViewPainelSimulado())
        await self.tree.sync()

bot = GustavoLMS()

# --- COMANDOS COM DESCRIÇÃO ---

@bot.tree.command(name="hub", description="Acessa a biblioteca de resumos e aulas.")
async def hub(interaction: discord.Interaction):
    await interaction.response.send_message(embed=discord.Embed(title="🏛️ Campus Virtual", description="Escolha uma área de estudo:", color=0x8e44ad), view=PainelCursos(), ephemeral=True)

@bot.tree.command(name="setup_simulado", description="Configura o painel fixo de criação de salas de prova.")
@app_commands.checks.has_permissions(administrator=True)
async def setup_simulado(interaction: discord.Interaction):
    await interaction.response.send_message("Painel de simulados ativado!", ephemeral=True)
    await interaction.channel.send(embed=discord.Embed(title="📝 Central de Simulados", description="Clique abaixo para abrir sua sala de prova privada.", color=0x3498db), view=ViewPainelSimulado())

@bot.tree.command(name="helpaluno", description="Mostra o guia de comandos para estudantes.")
async def helpaluno(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 Guia do Aluno", color=0x2ecc71)
    embed.add_field(name="/hub", value="Lê resumos e materiais.", inline=False)
    embed.add_field(name="/status", value="Vê seu nível e XP.", inline=False)
    embed.add_field(name="/tabela_verdade", value="Treina lógica proposicional.", inline=False)
    embed.add_field(name="/ranking", value="Vê os melhores da turma.", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="helpprof", description="Detalhes de todas as funções para os alunos.")
async def helpprof(interaction: discord.Interaction):
    embed = discord.Embed(title="📚 Manual do Estudante", description="Como usar o bot:", color=0x3498db)
    embed.add_field(name="/hub", value="Lê resumos e conteúdos.", inline=False)
    embed.add_field(name="/status", value="Vê seu nível e XP.", inline=False)
    embed.add_field(name="/ranking", value="Top 5 melhores alunos.", inline=False)
    embed.add_field(name="/duvida", value="Posta uma pergunta para a turma responder.", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="status", description="Mostra seu nível e progresso acadêmico.")
async def status(interaction: discord.Interaction):
    xp = pegar_xp(interaction.user.id)
    embed = discord.Embed(title="📊 Status Acadêmico", color=0x2c3e50)
    embed.add_field(name="Nível", value=f"✨ Lvl {xp//100}", inline=True)
    embed.add_field(name="XP Atual", value=f"⭐ {xp} XP", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ranking", description="Exibe o Top 5 alunos com mais XP.")
async def ranking(interaction: discord.Interaction):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('SELECT user_id, xp FROM alunos ORDER BY xp DESC LIMIT 5'); top = c.fetchall(); conn.close()
    embed = discord.Embed(title="🏆 Ranking da Turma", color=0xf1c40f)
    for i, (u, x) in enumerate(top): embed.add_field(name=f"{i+1}º Lugar", value=f"<@{u}>: {x} XP", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="tabela_verdade", description="Treine lógica resolvendo tabelas verdade.")
async def tabela_verdade(interaction: discord.Interaction):
    d = random.choice([
        {"t": "Conjunção (E)", "e": "p ∧ q", "r": ["V", "F", "F", "F"]},
        {"t": "Disjunção (OU)", "e": "p ∨ q", "r": ["V", "V", "V", "F"]},
        {"t": "Condicional (SE... ENTÃO)", "e": "p → q", "r": ["V", "F", "V", "V"]},
        {"t": "Bicondicional (SE E SOMENTE SE)", "e": "p ↔ q", "r": ["V", "F", "F", "V"]},
        {"t": "Disjunção Exclusiva (OU... OU)", "e": "p ⊕ q", "r": ["F", "V", "V", "F"]},
        {"t": "Negação da Conjunção (NAND)", "e": "¬(p ∧ q)", "r": ["F", "V", "V", "V"]},
        {"t": "Negação da Disjunção (NOR)", "e": "¬(p ∨ q)", "r": ["F", "F", "F", "V"]}
    ])
    await interaction.response.send_modal(ModalTabelaVerdade(d["t"], d["e"], d["r"]))

@bot.tree.command(name="backup", description="Baixa o arquivo de dados (Apenas ADM).")
@app_commands.checks.has_permissions(administrator=True)
async def backup(interaction: discord.Interaction):
    try: await interaction.response.send_message(file=discord.File(DB_PATH), ephemeral=True)
    except: await interaction.response.send_message("❌ Erro no backup.", ephemeral=True)

@bot.tree.command(name="helpdiretor", description="[ADM] Manual secreto apenas para o Diretor.")
@app_commands.checks.has_permissions(administrator=True)
async def helpdiretor(interaction: discord.Interaction):
    embed = discord.Embed(title="🛡️ Painel do Diretor", color=0xe74c3c)
    embed.add_field(name="/setup_simulado", value="Cria o painel fixo de provas.", inline=False)
    embed.add_field(name="/backup", value="Baixa o banco de dados.", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="resetar_meu_progresso", description="[ADM] Reseta TODO o seu histórico de questões.")
@app_commands.checks.has_permissions(administrator=True)
async def resetar_meu_progresso(interaction: discord.Interaction):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Deleta TUDO o que estiver ligado ao seu ID, sem filtrar matéria
    c.execute('DELETE FROM questoes_resolvidas WHERE user_id = ?', (str(interaction.user.id),))
    conn.commit()
    conn.close()
    await interaction.response.send_message("✅ Seu histórico foi totalmente resetado! Agora o bot vai ler as questões do JSON do zero.", ephemeral=True)

@bot.tree.command(name="duvida", description="Publique uma dúvida para a turma ajudar!")
async def duvida(interaction: discord.Interaction, pergunta: str):
    embed = discord.Embed(title="🚨 Dúvida de Aluno!", description=f"**Pergunta:**\n{pergunta}", color=0xf1c40f)
    # Foto do aluno que perguntou
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None)
    
    await interaction.response.send_message(content="@here Temos um colega com dúvida!", embed=embed)

async def main():
    print("⏳ Iniciando bot em 15s...")
    await asyncio.sleep(15)
    async with bot: await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())