import streamlit as st
import random
import time

# ==========================================
# 1. 게임 로직 및 초정밀 AI
# ==========================================
class DavinciCodeLogic:
    @staticmethod
    def init_game():
        if 'deck' not in st.session_state:
            # 0-11 흑/백 총 24개 (조커 없음)
            deck = []
            for color in ['B', 'W']:
                for i in range(12):
                    deck.append({'color': color, 'value': str(i), 'revealed': False})
            random.shuffle(deck)
            st.session_state.deck = deck
            st.session_state.player_names = ['나 (User)', '봇 1', '봇 2', '봇 3']
            st.session_state.players = {name: [] for name in st.session_state.player_names}
            st.session_state.turn_idx = 0
            st.session_state.log = ["🎮 게임 시작!"]
            st.session_state.status_msg = "당신의 차례입니다! 타일을 분석하세요."
            st.session_state.status_type = "info"

            # 인당 6개씩 배분
            for name in st.session_state.player_names:
                for _ in range(6):
                    st.session_state.players[name].append(st.session_state.deck.pop())
                # 정렬: 숫자순 -> 검은색(B) 우선
                st.session_state.players[name].sort(key=lambda x: (int(x['value']), 0 if x['color'] == 'B' else 1))

    @staticmethod
    def ai_ultra_think(bot_name):
        """남은 숫자를 전수 조사하여 가장 확률 높은 타일을 공격"""
        # 1. 봇이 알 수 있는 정보 (본인 패 + 전체 공개된 패)
        known_pool = []
        for name, hand in st.session_state.players.items():
            for t in hand:
                if name == bot_name or t['revealed']:
                    known_pool.append(f"{t['color']}{t['value']}")

        # 2. 공격 대상 선정
        targets = [n for n in st.session_state.player_names if n != bot_name]
        living_targets = [n for n in targets if any(not t['revealed'] for t in st.session_state.players[n])]
        if not living_targets: return None, None, None, ""
        
        best_target = None
        best_idx = None
        best_guess = None
        highest_confidence = -1
        best_reason = ""

        # 3. 모든 생존자의 모든 가려진 타일을 전수 조사
        for t_p in living_targets:
            hand = st.session_state.players[t_p]
            for idx, tile in enumerate(hand):
                if tile['revealed']: continue

                # 범위 계산
                min_v, max_v = -1, 12
                for i in range(idx - 1, -1, -1):
                    if hand[i]['revealed']: min_v = int(hand[i]['value']); break
                for i in range(idx + 1, len(hand)):
                    if hand[i]['revealed']: max_v = int(hand[i]['value']); break
                
                # 가능한 후보 필터링
                candidates = [str(v) for v in range(min_v + 1, max_v) 
                              if f"{tile['color']}{v}" not in known_pool]
                
                if candidates:
                    confidence = 100 // len(candidates)
                    # 가장 확신이 높은(후보가 적은) 타일을 타겟팅
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        best_target = t_p
                        best_idx = idx
                        best_guess = random.choice(candidates)
                        best_reason = f"확률 {confidence}% ({len(candidates)}개 후보 중 선택)"
                        if confidence == 100: break # 100% 찾으면 즉시 중단
            if highest_confidence == 100: break

        return best_target, best_idx, best_guess, best_reason

    @staticmethod
    def handle_guess(attacker, defender, idx, val):
        target_tile = st.session_state.players[defender][idx]
        if target_tile['value'] == val:
            target_tile['revealed'] = True
            st.session_state.status_msg = f"🟢 정답입니다! {attacker}가 {defender}의 {idx+1}번 타일을 맞췄습니다."
            st.session_state.status_type = "success"
            st.session_state.log.insert(0, st.session_state.status_msg)
            return True
        else:
            st.session_state.status_msg = f"🔴 틀렸습니다! {attacker}가 {defender}의 {idx+1}번을 {val}라고 잘못 추리했습니다."
            st.session_state.status_type = "error"
            st.session_state.log.insert(0, st.session_state.status_msg)
            return False

# ==========================================
# 2. UI 및 레이아웃 (정렬 고정)
# ==========================================
st.set_page_config(page_title="Davinci Code: Ultra AI", layout="wide")
DavinciCodeLogic.init_game()

st.markdown("""
    <style>
    .game-container { max-width: 1000px; margin: auto; }
    .player-row { 
        background: #f9f9f9; padding: 15px; border-radius: 10px; 
        margin-bottom: 10px; border-left: 5px solid #ccc;
    }
    .current-turn { border-left: 5px solid #00FFAA !important; background: #eefffb !important; }
    .tile-wrapper { display: flex; gap: 8px; margin-top: 10px; }
    .tile {
        width: 45px; height: 70px; border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px; font-weight: bold; border: 2px solid #333;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .B { background: #222; color: white; }
    .W { background: #fff; color: #222; }
    .revealed { border-color: #FF4B4B !important; color: #FF4B4B !important; background: #ffebeb; }
    .B.revealed { background: #441111; color: #FF4B4B !important; }
    </style>
""", unsafe_allow_html=True)

# 결과 알림바
if st.session_state.status_type == "success": st.success(st.session_state.status_msg)
elif st.session_state.status_type == "error": st.error(st.session_state.status_msg)
else: st.info(st.session_state.status_msg)

# ==========================================
# 3. 보드 렌더링 (구조 고정)
# ==========================================
st.markdown('<div class="game-container">', unsafe_allow_html=True)
for name in st.session_state.player_names:
    is_me = (name == '나 (User)')
    is_curr = (name == st.session_state.player_names[st.session_state.turn_idx])
    
    turn_class = "current-turn" if is_curr else ""
    st.markdown(f'<div class="player-row {turn_class}">', unsafe_allow_html=True)
    st.markdown(f"**{name}** {'(차례)' if is_curr else ''}")
    
    cols = st.columns(12) # 최대 12개 타일 수용 가능한 그리드 고정
    for i, t in enumerate(st.session_state.players[name]):
        rev_style = "revealed" if t['revealed'] else ""
        display_val = t['value'] if (t['revealed'] or is_me) else "?"
        cols[i].markdown(f'<div class="tile {t["color"]} {rev_style}">{display_val}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ==========================================
# 4. 컨트롤 로직 (이미 맞춘 타일 차단)
# ==========================================
curr_player = st.session_state.player_names[st.session_state.turn_idx]

if curr_player == '나 (User)':
    st.subheader("🎯 당신의 차례: 추리할 대상을 선택하세요.")
    c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
    
    with c1:
        target_p = st.selectbox("공격 대상", [n for n in st.session_state.player_names if n != '나 (User)'])
    with c2:
        # 핵심: 아직 안 까진(revealed=False) 타일만 선택 가능하도록 필터링
        available_indices = [i for i, t in enumerate(st.session_state.players[target_p]) if not t['revealed']]
        if available_indices:
            t_idx = st.selectbox("타일 위치 선택", available_indices, format_func=lambda x: f"{x+1}번 타일")
        else:
            st.warning("이 플레이어의 타일이 모두 공개되었습니다!")
            t_idx = None
    with c3:
        guess_v = st.text_input("숫자(0-11)")
    with c4:
        st.write("")
        if st.button("🔥 추리 제출", use_container_width=True) and t_idx is not None:
            if guess_v.strip().isdigit():
                hit = DavinciCodeLogic.handle_guess('나 (User)', target_p, t_idx, guess_v.strip())
                if not hit:
                    st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
                st.rerun()

else:
    st.subheader(f"🤖 {curr_player}가 데이터를 연산 중입니다...")
    if st.button(f"{curr_player} 행동 완료", use_container_width=True):
        time.sleep(0.3)
        target_p, t_idx, g_val, reason = DavinciCodeLogic.ai_ultra_think(curr_player)
        if target_p is not None:
            st.session_state.log.insert(0, f"🧠 {curr_name} 분석: {target_p}의 {t_idx+1}번은 {g_val} ({reason})")
            hit = DavinciCodeLogic.handle_guess(curr_player, target_p, t_idx, g_val)
            if not hit:
                st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()

with st.sidebar:
    st.title("🛡️ 로그 센터")
    for l in st.session_state.log[:20]: st.caption(l)
    if st.button("🔄 새 게임 시작"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
