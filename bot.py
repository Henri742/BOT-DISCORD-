import discord
from discord import app_commands
from discord.ext import commands
import random
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

# --- 1. COMPONENTES DE INTERFACE (UI) ---

class MenuGlossario(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="API", description="Ponte entre softwares", emoji="🔌"),
            discord.SelectOption(label="Git", description="Controle de versão", emoji="📚"),
            discord.SelectOption(label="Deploy", description="Colocar o bot online", emoji="🚀"),
            discord.SelectOption(label="Backend", description="Lógica de servidor", emoji="🧠"),
            discord.SelectOption(label="Frontend", description="Interface visual", emoji="🎨"),
        ]
        super().__init__(placeholder="Escolha um termo técnico...", options=options)

    async def callback(self, interaction: discord.Interaction):
        termos = {
            "API": "É um conjunto de regras que permite que um software 'fale' com outro. Ex: Seu bot falando com o Discord.",
            "Git": "Um sistema que salva versões do seu código. É a sua rede de segurança.",
            "Deploy": "Processo de subir seu código para um servidor (Railway) para ele rodar 24h.",
            "Backend": "A parte que o usuário não vê. Onde os dados são processados.",
            "Frontend": "Tudo o que é visual. Em bots, são os Embeds e Botões."
        }
        await interaction.response.send_message(f"**{self.values[0]}:** {termos[self.values[0]]}", ephemeral=True)

class ViewInterativa(discord.ui.View):
    def __init__(self, codigo_exemplo=None):
        super().__init__(timeout=None)
        self.codigo_exemplo = codigo_exemplo
        if not codigo_exemplo:
            self.remove_item(self.ver_solucao)

    @discord.ui.button(label="Ver Solução", style=discord.ButtonStyle.success, emoji="✅")
    async def ver_solucao(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"**Exemplo de código:**\n```python\n{self.codigo_exemplo}\n```", ephemeral=True
        )

# --- 2. CLASSE PRINCIPAL ---

class GustavoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True # Necessário para XP por usuário
        super().__init__(command_prefix="!", intents=intents)
        self.usuarios_xp = {}

    async def setup_hook(self):
        await self.tree.sync()
        print(f"[{datetime.datetime.now()}] ✅ Sistema sincronizado com sucesso.")

bot = GustavoBot()

# --- 3. COMANDOS ---

@bot.tree.command(name="glossario", description="Abre o menu de termos técnicos")
async def glossario(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(MenuGlossario())
    await interaction.response.send_message("📚 **O que você deseja aprender hoje?**", view=view)

@bot.tree.command(name="treinar", description="Receba um desafio de lógica")
async def treinar(interaction: discord.Interaction):
    desafios = [
        {"p": "Crie uma lista de 5 números e mostre a soma deles.", "c": "nums = [1,2,3,4,5]\nprint(sum(nums))"},
        {"p": "Crie um 'if' que verifica se uma idade é maior que 18.", "c": "idade = 20\nif idade >= 18:\n    print('Maior de idade')"},
        {"p": "Faça um loop que imprima 'Python' 5 vezes.", "c": "for i in range(5):\n    print('Python')"}
    ]
    escolhido = random.choice(desafios)
    
    # Sistema de XP simples
    uid = interaction.user.id
    bot.usuarios_xp[uid] = bot.usuarios_xp.get(uid, 0) + 15
    
    embed = discord.Embed(title="🎯 Desafio de Programação", color=0x2ecc71, timestamp=datetime.datetime.now())
    embed.description = f"**Tarefa:** {escolhido['p']}"
    embed.add_field(name="Recompensa", value="⭐ 15 XP")
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text=f"Seu XP Total: {bot.usuarios_xp[uid]}")
    
    view = ViewInterativa(codigo_exemplo=escolhido['c'])
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="status", description="Veja suas estatísticas e do servidor")
async def status(interaction: discord.Interaction):
    xp = bot.usuarios_xp.get(interaction.user.id, 0)
    latencia = round(bot.latency * 1000)
    
    embed = discord.Embed(title=f"📊 Status - {interaction.user.display_name}", color=0x3498db)
    embed.add_field(name="Seu XP", value=f"⭐ {xp}")
    embed.add_field(name="Nível", value=f"✨ {xp // 50}") # Cada 50 XP sobe um nível
    embed.add_field(name="Latência", value=f"📡 {latencia}ms")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="limpar", description="Limpa o chat (Apenas Admins)")
@app_commands.checks.has_permissions(manage_messages=True)
async def limpar(interaction: discord.Interaction, quantidade: int):
    if quantidade > 100:
        return await interaction.response.send_message("Máximo 100 mensagens!", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f"✅ {len(deleted)} mensagens removidas.", ephemeral=True)

# --- 4. TRATAMENTO DE ERROS ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("🚫 Você não tem permissão de Admin para isso!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"🚀 GUSTAVO MASTER ONLINE")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="seu código..."))

bot.run(os.getenv("DISCORD_TOKEN"))