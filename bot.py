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
# 🗄️ BANCO DE DADOS (USANDO VOLUME /data)
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

def resetar_resolvidas(user_id, materia):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('DELETE FROM questoes_resolvidas WHERE user_id = ? AND materia = ?', (str(user_id), materia))
    conn.commit(); conn.close()

# ==========================================
# 🖥️ COMPONENTES VISUAIS
# ==========================================

try:
    with open('conteudo.json', 'r', encoding='utf-8') as f:
        DADOS = json.load(f)
except:
    DADOS = {"resumos": {}, "questoes": {}}

class DropdownResumos(discord.ui.Select):
    def __init__(self, curso):
        self.curso = curso
        opcoes = [discord.SelectOption(label=k) for k in DADOS["resumos"].get(curso, {}).keys()] or [discord.SelectOption(label="Vazio")]
        super().__init__(placeholder="Selecione a aula...", options=opcoes)
    async def callback(self, interaction: discord.Interaction):
        texto = DADOS["resumos"][self.curso].get(self.values[0], "Conteúdo não encontrado.")
        await interaction.response.edit_message(embed=discord.Embed(title=f"📖 {self.values[0]}", description=texto, color=0x3498db))

class PainelCursos(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Matemática Aplicada", style=discord.ButtonStyle.primary, emoji="🔢")
    async def btn_ma(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos:", view=discord.ui.View().add_item(DropdownResumos("MA")), ephemeral=True)
    @discord.ui.button(label="Gestão de Times", style=discord.ButtonStyle.success, emoji="👥")
    async def btn_gt(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos:", view=discord.ui.View().add_item(DropdownResumos("GT")), ephemeral=True)

class ViewSimulado(discord.ui.View):
    def __init__(self, user_id, questoes, materia):
        super().__init__(timeout=600)
        self.user_id, self.questoes, self.materia = user_id, questoes, materia
        self.total, self.atual, self.pontos = len(questoes), 0, 0
    async def atualizar(self, interaction: discord.Interaction):
        if self.atual >= self.total:
            xp = self.pontos * 20; adicionar_xp(self.user_id, xp)
            embed = discord.Embed(title="📊 Resultado", description=f"Matéria: {self.materia}\nAcertos: {self.pontos}/{self.total}\nXP: +{xp}", color=0x2ecc71)
            try: await interaction.user.send(embed=embed)
            except: pass
            await interaction.response.edit_message(content="✅ Simulado concluído! O canal fechará em 10s.", embed=None, view=None)
            await asyncio.sleep(10); await interaction.channel.delete(); return
        q = self.questoes[self.atual]; registrar_questao(self.user_id, self.materia, q['q'])
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

class ViewPainelSimulado(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Iniciar Novo Simulado", style=discord.ButtonStyle.primary, emoji="📝", custom_id="persistent:iniciar")
    async def iniciar_sala(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True), interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        canal = await interaction.guild.create_text_channel(f"prova-{interaction.user.name}".lower(), overwrites=overwrites)
        await interaction.response.send_message(f"✅ Sala criada: {canal.mention}", ephemeral=True)
        await canal.send(embed=discord.Embed(title="🎒 Sala de Prova", description="Escolha a disciplina:", color=0x8e44ad), view=PainelCursos())

class ModalTabelaVerdade(discord.ui.Modal):
    l1 = discord.ui.TextInput(label='1. p=V, q=V', max_length=1)
    l2 = discord.ui.TextInput(label='2. p=V, q=F', max_length=1)
    l3 = discord.ui.TextInput(label='3. p=F, q=V', max_length=1)
    l4 = discord.ui.TextInput(label='4. p=F, q=F', max_length=1)
    def __init__(self, t, e, r): super().__init__(title=t[:45]); self.exp, self.resp = e, r
    async def on_submit(self, interaction: discord.Interaction):
        u = [self.l1.value.upper(), self.l2.value.upper(), self.l3.value.upper(), self.l4.value.upper()]
        if u == self.resp:
            adicionar_xp(interaction.user.id, 30)
            await interaction.response.send_message(f"✅ Correto! +30 XP")
        else: await interaction.response.send_message(f"❌ Errou! Gabarito: {', '.join(self.resp)}", ephemeral=True)

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

@bot.tree.command(name="setup_simulado")
@app_commands.checks.has_permissions(administrator=True)
async def setup_simulado(interaction: discord.Interaction):
    await interaction.response.send_message("Painel configurado!", ephemeral=True)
    await interaction.channel.send(embed=discord.Embed(title="📝 Central de Simulados", description="Clique abaixo para abrir uma sala privada.", color=0x3498db), view=ViewPainelSimulado())

@bot.tree.command(name="hub")
async def hub(interaction: discord.Interaction):
    await interaction.response.send_message(embed=discord.Embed(title="🏛️ Campus Virtual", description="Selecione a disciplina:", color=0x8e44ad), view=PainelCursos(), ephemeral=True)

@bot.tree.command(name="status")
async def status(interaction: discord.Interaction):
    xp = pegar_xp(interaction.user.id)
    embed = discord.Embed(title="📊 Status Académico", color=0x2c3e50)
    embed.add_field(name="Nível", value=f"✨ Lvl {xp//100}", inline=True)
    embed.add_field(name="XP Total", value=f"⭐ {xp} XP", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ranking")
async def ranking(interaction: discord.Interaction):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('SELECT user_id, xp FROM alunos ORDER BY xp DESC LIMIT 5'); top = c.fetchall(); conn.close()
    embed = discord.Embed(title="🏆 Top 5 Alunos", color=0xf1c40f)
    for i, (u, x) in enumerate(top): embed.add_field(name=f"{i+1}º", value=f"<@{u}>: {x} XP", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="calcular")
async def calcular(interaction: discord.Interaction, n1: float, op: str, n2: float):
    try: res = eval(f"{n1}{op}{n2}")
    except: res = "Erro"
    await interaction.response.send_message(f"🔢 Resultado: `{res}`")

@bot.tree.command(name="tabela_verdade")
async def tabela_verdade(interaction: discord.Interaction):
    d = random.choice([{"t": "Conjunção (E)", "e": "p ^ q", "r": ["V", "F", "F", "F"]}, {"t": "Disjunção (OU)", "e": "p v q", "r": ["V", "V", "V", "F"]}])
    await interaction.response.send_modal(ModalTabelaVerdade(d["t"], d["e"], d["r"]))

@bot.tree.command(name="backup")
@app_commands.checks.has_permissions(administrator=True)
async def backup(interaction: discord.Interaction):
    try: await interaction.response.send_message(file=discord.File(DB_PATH), ephemeral=True)
    except: await interaction.response.send_message("❌ Erro no backup.", ephemeral=True)

async def main():
    await asyncio.sleep(15)
    async with bot: await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())