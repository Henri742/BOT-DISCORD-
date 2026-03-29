import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import os
import datetime
from dotenv import load_dotenv

# ==========================================
# ⚙️ CONFIGURAÇÕES INICIAIS
# ==========================================
load_dotenv()

class GustavoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.usuarios_xp = {} # "Banco de dados" de XP temporário

    async def setup_hook(self):
        await self.tree.sync()
        print(f"[{datetime.datetime.now()}] 🚀 Gustavo Ultimate Sincronizado e Operante.")

bot = GustavoBot()

# ==========================================
# 📚 BANCOS DE DADOS DE CONHECIMENTO
# ==========================================

DICIONARIO_TECH = {
    "API": "Application Programming Interface. Ponte de comunicação entre dois sistemas.",
    "Git": "Sistema de controle de versão. A 'máquina do tempo' do seu código.",
    "Deploy": "Colocar o código em um servidor real (como o Railway) para rodar 24/7.",
    "Frontend": "A interface visual, onde o usuário clica e interage.",
    "Backend": "O servidor, banco de dados e a lógica 'invisível' por trás da aplicação."
}

DICIONARIO_ERROS = {
    "NameError": "Variável não definida. Você chamou algo que não existe ou digitou errado.",
    "SyntaxError": "Erro gramatical do Python. Esqueceu dois-pontos (:) ou fechamento de aspas?",
    "TypeError": "Operação inválida entre tipos. Ex: tentar somar texto ('A') com número (1).",
    "IndentationError": "Espaçamento incorreto. O Python exige 4 espaços (TAB) dentro de blocos."
}

FUNCOES_PYTHON = {
    "print()": "Exibe informações na tela do terminal.",
    "input()": "Pausa o código e espera o usuário digitar algo. Retorna sempre um texto (str).",
    "len()": "Conta a quantidade de itens em uma lista ou caracteres em um texto.",
    "type()": "Descobre o tipo de uma variável (int, float, str, bool).",
    "int()": "Converte um texto ou número decimal para número inteiro."
}

CONTEUDO_ACADEMICO = {
    "Logica_Matematica": {
        "Aula 01": "**Introdução:** Álgebra Booleana (George Boole). Processa dados via binários (V/F). Usada em circuitos digitais, Teoria dos Grafos e Criptografia.",
        "Aula 02": "**Axiomas:**\n1. Não Contradição (Não pode ser V e F juntos).\n2. Terceiro Excluído (Ou é V ou F, não há 3ª opção).\nProposições podem ser Simples (Atômicas) ou Compostas (Moleculares).",
        "Aula 03": "**Conectivos:**\n• `~` (Negação): Inverte\n• `^` (AND): Só V se tudo for V\n• `v` (OR): V se pelo menos um for V\n• `->` (Condicional): Só F na 'Vera Fischer' (V->F)\n• `<->` (Bicondicional): V se forem iguais.",
        "Aula 04": "**Tabela Verdade:**\nFórmula de linhas: $L = 2^n$.\nOrdem: Parênteses > Negação > E/OU > Condicionais."
    },
    "Logica_Programacao": {
        "Módulo 1-2": "**Algoritmos e Fluxogramas:** Sequência finita de passos lógicos. Fluxogramas usam Losangos (Decisão) e Retângulos (Processo).",
        "Módulo 3-4": "**Loops e Controle:**\n• `Para` (For): Repetição com fim conhecido.\n• `Enquanto` (While): Repete sob uma condição verdadeira.\n• `Repita`: Faz primeiro, checa depois.",
        "Módulo 5": "**Python Base:** Tipagem Dinâmica (não precisa declarar `int x`). O `#` é usado para fazer comentários ignorados pelo computador.",
        "Módulo 6": "**Condicionais Python:**\n`if` (Se), `elif` (Senão Se), `else` (Senão). Usado intensamente para cálculo de médias e aprovações."
    }
}

# ==========================================
# 🖥️ COMPONENTES DE INTERFACE (UI) E MODAIS
# ==========================================

# Modal (Pop-up) para a Calculadora da Aula 06 do Prof. Marcelo
class CalculadoraMediaModal(discord.ui.Modal, title='Calculadora de Média (Aula 06)'):
    nota1 = discord.ui.TextInput(label='Nota 1', placeholder='Ex: 7.5')
    nota2 = discord.ui.TextInput(label='Nota 2', placeholder='Ex: 5.0')

    async def on_submit(self, interaction: discord.Interaction):
        try:
            n1 = float(self.nota1.value.replace(',', '.'))
            n2 = float(self.nota2.value.replace(',', '.'))
            media = (n1 + n2) / 2
            
            if media >= 7.0:
                status = "✅ APROVADO"
                cor = 0x2ecc71
            elif media >= 4.0:
                status = "⚠️ REAVALIAÇÃO (Recuperação)"
                cor = 0xf1c40f
            else:
                status = "❌ REPROVADO"
                cor = 0xe74c3c

            embed = discord.Embed(title="Resultado Acadêmico", color=cor)
            embed.add_field(name="Média Final", value=f"**{media:.1f}**")
            embed.add_field(name="Situação", value=status)
            await interaction.response.send_message(embed=embed)
        except ValueError:
            await interaction.response.send_message("❌ Por favor, digite apenas números válidos!", ephemeral=True)

class MenuAcademico(discord.ui.Select):
    def __init__(self, curso):
        self.curso = curso
        if curso == "matematica":
            options = [discord.SelectOption(label=k, value=k, emoji="📐") for k in CONTEUDO_ACADEMICO["Logica_Matematica"].keys()]
        else:
            options = [discord.SelectOption(label=k, value=k, emoji="💻") for k in CONTEUDO_ACADEMICO["Logica_Programacao"].keys()]
        super().__init__(placeholder="Selecione o módulo de estudo...", options=options)

    async def callback(self, interaction: discord.Interaction):
        banco = CONTEUDO_ACADEMICO["Logica_Matematica"] if self.curso == "matematica" else CONTEUDO_ACADEMICO["Logica_Programacao"]
        embed = discord.Embed(title=f"📖 Resumo: {self.values[0]}", description=banco[self.values[0]], color=0x3498db)
        await interaction.response.edit_message(embed=embed)

class AcervoView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="Lógica Matemática (Anderlan)", style=discord.ButtonStyle.primary)
    async def btn_mat(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View()
        view.add_item(MenuAcademico("matematica"))
        await interaction.response.send_message("Módulos de Matemática:", view=view, ephemeral=True)

    @discord.ui.button(label="Lógica Programação (Marcelo)", style=discord.ButtonStyle.success)
    async def btn_prog(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View()
        view.add_item(MenuAcademico("programacao"))
        await interaction.response.send_message("Módulos de Programação:", view=view, ephemeral=True)

# ==========================================
# 🚀 COMANDOS DO BOT (SLASH COMMANDS)
# ==========================================

@bot.tree.command(name="ajuda", description="O painel central de comandos do bot.")
async def ajuda(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Gustavo Ultimate - Central de Comando", color=0x9b59b6)
    embed.add_field(name="📚 Acadêmico", value="`/estudar` - Resumo dos PDFs\n`/media` - Calculadora de Notas\n`/quiz` - Teste seus conhecimentos", inline=False)
    embed.add_field(name="💻 Programação", value="`/glossario` - Termos Tech\n`/erros` - Guia de Erros Python\n`/funcoes` - Funções Nativas", inline=False)
    embed.add_field(name="🛠️ Ferramentas", value="`/pomodoro` - Timer de estudo\n`/status` - Veja seu XP e Ping\n`/limpar` - Deleta mensagens", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="estudar", description="Acesse todo o resumo dos PDFs dos professores.")
async def estudar(interaction: discord.Interaction):
    embed = discord.Embed(title="📚 Acervo Universitário", description="Selecione a disciplina abaixo:", color=0xf1c40f)
    await interaction.response.send_message(embed=embed, view=AcervoView())

@bot.tree.command(name="media", description="Calcula se você foi aprovado (Aula 06 Prof. Marcelo).")
async def media(interaction: discord.Interaction):
    # Abre a janela Pop-up Modal
    await interaction.response.send_modal(CalculadoraMediaModal())

@bot.tree.command(name="glossario", description="Consulte termos técnicos de tecnologia.")
@app_commands.choices(termo=[app_commands.Choice(name=k, value=k) for k in DICIONARIO_TECH.keys()])
async def glossario(interaction: discord.Interaction, termo: str):
    await interaction.response.send_message(f"**{termo}**: {DICIONARIO_TECH[termo]}")

@bot.tree.command(name="erros", description="Explica os erros mais comuns do Python.")
@app_commands.choices(erro=[app_commands.Choice(name=k, value=k) for k in DICIONARIO_ERROS.keys()])
async def erros(interaction: discord.Interaction, erro: str):
    await interaction.response.send_message(f"🚨 **{erro}**\n{DICIONARIO_ERROS[erro]}")

@bot.tree.command(name="funcoes", description="Explica as funções nativas do Python.")
@app_commands.choices(funcao=[app_commands.Choice(name=k, value=k) for k in FUNCOES_PYTHON.keys()])
async def funcoes(interaction: discord.Interaction, funcao: str):
    await interaction.response.send_message(f"🛠️ **{funcao}**: {FUNCOES_PYTHON[funcao]}")

@bot.tree.command(name="quiz", description="Ganha XP respondendo perguntas dos PDFs.")
async def quiz(interaction: discord.Interaction):
    perguntas = [
        {"q": "Qual conectivo só é Falso no caso V->F?", "a": "Condicional (Vera Fischer)"},
        {"q": "Qual a fórmula das linhas da tabela verdade?", "a": "L = 2^n"},
        {"q": "Qual função converte texto em inteiro no Python?", "a": "int()"}
    ]
    p = random.choice(perguntas)
    
    # Dá 20 XP para o usuário
    uid = interaction.user.id
    bot.usuarios_xp[uid] = bot.usuarios_xp.get(uid, 0) + 20

    embed = discord.Embed(title="🎯 Quiz Valendo XP", description=p["q"], color=0xe67e22)
    embed.set_footer(text="Você ganhou +20 XP ao solicitar este quiz!")
    
    class ViewResp(discord.ui.View):
        @discord.ui.button(label="Revelar Resposta", style=discord.ButtonStyle.secondary)
        async def revelar(self, i: discord.Interaction, b: discord.ui.Button):
            await i.response.send_message(f"✅ **Resposta:** {p['a']}", ephemeral=True)
            
    await interaction.response.send_message(embed=embed, view=ViewResp())

@bot.tree.command(name="pomodoro", description="Inicia um timer de foco de 25 minutos.")
async def pomodoro(interaction: discord.Interaction):
    await interaction.response.send_message("🍅 **Pomodoro Iniciado!** Foque nos estudos por 25 minutos. Eu te aviso quando acabar.")
    # Espera 25 minutos (25 * 60 segundos)
    await asyncio.sleep(1500)
    await interaction.followup.send(f"⏰ {interaction.user.mention}, o tempo acabou! Faça uma pausa de 5 minutos.")

@bot.tree.command(name="status", description="Veja seu Nível, XP e o Ping do Bot.")
async def status(interaction: discord.Interaction):
    xp = bot.usuarios_xp.get(interaction.user.id, 0)
    embed = discord.Embed(title="📊 Status do Jogador", color=0x2c3e50)
    embed.add_field(name="Nível Atual", value=f"✨ Lvl {xp // 100}")
    embed.add_field(name="XP Total", value=f"⭐ {xp} XP")
    embed.add_field(name="Ping do Servidor", value=f"📡 {round(bot.latency * 1000)}ms")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="limpar", description="[Admin] Limpa até 100 mensagens do chat.")
@app_commands.checks.has_permissions(manage_messages=True)
async def limpar(interaction: discord.Interaction, quantidade: int):
    await interaction.response.defer(ephemeral=True)
    apagadas = await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f"🧹 Chat limpo! {len(apagadas)} mensagens deletadas.", ephemeral=True)

# ==========================================
# 🚀 INICIALIZAÇÃO
# ==========================================
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Prof. Marcelo & Anderlan"))

bot.run(os.getenv("DISCORD_TOKEN"))