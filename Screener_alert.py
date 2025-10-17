# Nama File: screener_alert.py

import pandas as pd
import yfinance as yf
import pandas_ta as ta
import requests # Library baru untuk mengirim alert

# --- MASUKKAN DATA ANDA DI SINI ---
TELEGRAM_TOKEN = "GANTI_DENGAN_TOKEN_BOT_ANDA"
TELEGRAM_CHAT_ID = "GANTI_DENGAN_CHAT_ID_ANDA"
# -----------------------------------

# --- PENGATURAN SCREENER ---
CONSOLIDATION_PERIOD = 20
VOLUME_SPIKE_FACTOR = 1.5
TARGET_PROFIT_PERCENT = 0.025

DAFTAR_IDX80 = [
    'ACES.JK', 'ADMR.JK', 'ADRO.JK', 'AKRA.JK', 'AMMN.JK', 'AMRT.JK', 'ANTM.JK', 'ARTO.JK', 'ASII.JK', 'ASSA.JK',
    'AUTO.JK', 'BBCA.JK', 'BBNI.JK', 'BBRI.JK', 'BBTN.JK', 'BFIN.JK', 'BMRI.JK', 'BNGA.JK', 'BRIS.JK', 'BRPT.JK',
    'BSDE.JK', 'BUKA.JK', 'CIMB.JK', 'CPIN.JK', 'CTRA.JK', 'DOID.JK', 'DSNG.JK', 'EMTK.JK', 'ENRG.JK', 'ERAA.JK',
    'ESSA.JK', 'EXCL.JK', 'FILM.JK', 'GGRM.JK', 'GOTO.JK', 'HRUM.JK', 'ICBP.JK', 'IMAS.JK', 'INCO.JK', 'INDF.JK',
    'INDY.JK', 'INKP.JK', 'INTP.JK', 'ISAT.JK', 'ITMG.JK', 'JSMR.JK', 'KLBF.JK', 'MAPA.JK', 'MAPI.JK', 'MBMA.JK',
    'MDKA.JK', 'MEDC.JK', 'MIKA.JK', 'MNCN.JK', 'MTEL.JK', 'MYOR.JK', 'NISP.JK', 'PBSA.JK', 'PGAS.JK', 'PGEO.JK',
    'PNBN.JK', 'PNLF.JK', 'PTBA.JK', 'PTPP.JK', 'PWON.JK', 'PYFA.JK', 'SIDO.JK', 'SILO.JK', 'SMGR.JK', 'SMRA.JK',
    'SRTG.JK', 'SSMS.JK', 'TBIG.JK', 'TINS.JK', 'TKIM.JK', 'TLKM.JK', 'TOWR.JK', 'TPIA.JK', 'UNTR.JK', 'UNVR.JK'
]
ALL_STOCKS = sorted(list(set(DAFTAR_IDX80)))

# --- FUNGSI BARU: Mengirim Alert ke Telegram ---
def send_telegram_alert(message):
    """Mengirim pesan ke bot Telegram Anda."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Gagal mengirim alert: {e}")
        return None

# --- FUNGSI SCREENER (HAMPIR SAMA SEPERTI SEBELUMNYA) ---
def screen_stocks():
    print(f"Memulai proses screening untuk {len(ALL_STOCKS)} saham...")
    
    for ticker in ALL_STOCKS:
        try:
            # (Logika screening lainnya tetap sama...)
            data_intraday = yf.download(tickers=ticker, period='10d', interval='15m', progress=False, show_errors=False)
            if data_intraday.empty or len(data_intraday) < 50: continue

            avg_daily_value = (data_intraday['Close'] * data_intraday['Volume']).rolling(window=96).mean().iloc[-1]
            if avg_daily_value < 2_000_000_000: continue
            
            data_intraday.ta.ema(length=50, append=True)
            data_intraday.ta.macd(append=True)
            last_row_intraday = data_intraday.iloc[-1]

            highest_in_consolidation = data_intraday['High'].iloc[-CONSOLIDATION_PERIOD-1:-1].max()
            is_breakout = last_row_intraday['Close'] > highest_in_consolidation
            average_volume = data_intraday['Volume'].iloc[-CONSOLIDATION_PERIOD-1:-1].mean()
            has_volume_spike = last_row_intraday['Volume'] > average_volume * VOLUME_SPIKE_FACTOR
            above_ema50_intraday = last_row_intraday['Close'] > last_row_intraday['EMA_50']
            macd_bullish_intraday = last_row_intraday['MACD_12_26_9'] > last_row_intraday['MACDs_12_26_9']

            if (is_breakout and has_volume_spike and above_ema50_intraday and macd_bullish_intraday):
                # Jika sebuah saham lolos, buat pesan alert
                entry_price = last_row_intraday['Close']
                target_profit = entry_price * (1 + TARGET_PROFIT_PERCENT)
                stop_loss = data_intraday['Low'].iloc[-CONSOLIDATION_PERIOD-1:-1].min()

                message = (
                    f"<b>🔔 Sinyal Trading Terdeteksi! 🔔</b>\n\n"
                    f"<b>Saham:</b> ${ticker.replace('.JK', '')}\n"
                    f"<b>Sinyal:</b> Breakout + Volume Spike\n\n"
                    f"<b>--TRADING PLAN--</b>\n"
                    f"<b>Area Beli:</b> {entry_price:.0f}\n"
                    f"<b>Target Profit:</b> {target_profit:.0f}\n"
                    f"<b>Stop Loss:</b> {stop_loss:.0f}\n\n"
                    f"<i>Harap lakukan verifikasi BrokSum & Candle sebelum eksekusi.</i>"
                )
                
                # Kirim alert!
                send_telegram_alert(message)
                print(f"✅ Alert untuk ${ticker.replace('.JK', '')} berhasil dikirim!")

        except Exception as e:
            continue
            
    print("Proses screening selesai.")

# --- Jalankan fungsi utama ---
if __name__ == '__main__':

    screen_stocks()
