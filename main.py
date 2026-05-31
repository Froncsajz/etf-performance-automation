import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Dátumsorozat generálása ami csak a munkanapokat tartalmazza (freq = 'B' --> Business Days)
dates = pd.date_range(start="2025-01-01", end="2026-05-29", freq="B")
trading_days = 252
np.random.seed(26)


# Évesített hozamok és kockázatok (szórás) alapján számolunk, logaritmikus logikával
def generate_etf_prices(start_price, annual_return, annual_volatility, days):
    dt = 1 / 252  # 1 munkanap az évből

    # Kiszámoljuk a napi szintű várható értéket és szórást
    # A volatilitás-korrekció (-0.5 * volatility^2) megakadályozza az elszállást!
    daily_drift = (annual_return - 0.5 * annual_volatility ** 2) * dt
    daily_vol = annual_volatility * np.sqrt(dt)

    # Legeneráljuk a logaritmikus hozamokat (ezeket össze lehet adni!)
    log_returns = np.random.normal(daily_drift, daily_vol, days)

    # Az összeadott hozamokat a végén emeljük exponenciális hatványra (e^x)
    price_trajectory = start_price * np.exp(np.cumsum(log_returns))
    return price_trajectory


simulated_data = {
    # IVV (S&P 500): 500$-ról indul, 12% éves elvárt hozam, 15% éves kockázat
    'iShares_Core_SP500 (IVV)': generate_etf_prices(500, 0.12, 0.15, len(dates)),

    # URTH (MSCI World): 120$-ról indul, 10% éves elvárt hozam, 14% éves kockázat
    'iShares_MSCI_World (URTH)': generate_etf_prices(120, 0.10, 0.14, len(dates)),

    # AGG (Kötvény): 100$-ról indul, 4% éves elvárt hozam, 5% éves kockázat (nagyon stabil!)
    'iShares_Core_Bond (AGG)': generate_etf_prices(100, 0.04, 0.05, len(dates))
}

df = pd.DataFrame(simulated_data, index=dates)

#adatok szabotálázsa az adattisztító funkciók érdemi használatához
df.iloc[15,0 ]= np.nan
df.iloc[150,1] *= 1.5

# A) Hiányzó adatok kitöltése előrevetítéssel
df.ffill(inplace=True)

# B) Mozaik-stílusú szűrés: csak a MÚLTBELI 10 napot nézzük (closed='left')
# Így a mai tüske nem tudja eltorzítani a saját átlagát és szórását!
rolling_mean = df.shift(1).rolling(window=10, min_periods=1).mean()
rolling_std = df.shift(1).rolling(window=10, min_periods=1).std()

for col in df.columns:
    # Kiválasztjuk azokat a pontokat, amik több mint 3 szórással térnek el a TISZTA múltbeli átlagtól
    anomalies = (df[col] > rolling_mean[col] + 3 * rolling_std[col]) & (rolling_std[col] > 0)

    # Kisimítjuk a tüskét: Mivel a rolling_mean[col] most már egy teljesen tiszta,
    # tüske-mentes múltbeli átlag, erre cserélve a vonal tökéletesen simulni fog!
    df.loc[anomalies, col] = rolling_mean[col]

print("QA Pipeline sikeresen lefutott. Az adatok tiszták!")


daily_returns = df.pct_change().dropna()

# Kiszámoljuk az évesített hozamot százalékban
annualized_return = daily_returns.mean() * trading_days * 100

# Kiszámoljuk az évesített kockázatot (szórást) százalékban
annualized_variance = daily_returns.std()**2 * trading_days
annualized_volatility = np.sqrt(annualized_variance)

# Kiszámoljuk a Sharpe-rátát
sharpe_ratio = (daily_returns.mean() * trading_days) / annualized_volatility

performance_summary = pd.DataFrame({
    'Annualized Return (%)': annualized_return,
    'Annualized Volatility (%)': annualized_volatility,
    'Sharpe Ratio': sharpe_ratio
})

print(performance_summary)

# Kiszámoljuk a teljes időszakra vetített felhalmozott növekedést
cumulative_returns = (1 + daily_returns).cumprod() - 1

# 1. Létrehozunk egy optimális méretű grafikon ablakot (12x6 hüvelyk)
plt.figure(figsize=(12, 6))

# 2. Egy ciklussal végigmegyünk az ETF-ek oszlopain, és mindegyik vonalát felrajzoljuk
for col in cumulative_returns.columns:
    # A függőleges tengelyre a százalékos hozamot tesszük (* 100), a vízszintesre a dátumokat
    plt.plot(cumulative_returns.index, cumulative_returns[col] * 100, label=col, linewidth=2)

# 3. Professzionális dizájnelemek hozzáadása
plt.title('iShares ETF Product Suite - Cumulative Performance Analysis (2025-2026)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Growth of Investment (%)', fontsize=12)

# Jelmagyarázat elhelyezése (hogy tudjuk, melyik szín melyik ETF)
plt.legend(loc='upper left', fontsize=10)

# Halvány, szaggatott rácsháló a pontos értékek leolvasásához
plt.grid(True, linestyle='--', alpha=0.5)

# Automatikus térköz-igazítás, hogy a feliratok és dátumok ne lógjanak le a képről
plt.tight_layout()

# 4. AUTOMATIKUS MENTÉS: Elmentjük a kész grafikont egy nagy felbontású képfájlba
plt.savefig('ishares_portfolio_growth.png', dpi=300)
plt.close()

print("\n[SUCCESS] A grafikus ügyfélriport elmentve: 'ishares_portfolio_growth.png' néven!")


