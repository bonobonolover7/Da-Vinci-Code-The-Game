import streamlit as st
import random
import time

# ==========================================
# 1. 게임 로직 및 초정밀 AI 클래스
# ==========================================
class DavinciCodeLogic:
    @staticmethod
    def init_game():
        needed_keys = ['deck', 'players', 'player_names', 'turn_idx', 'log', 'target_idx', 'status_msg', 'status_type']
        if not all(key in st.session_state for key in needed_keys):
            deck = []
            for color in ['B', 'W']:
                for i in range(12):
                    deck.append({'color': color, 'value': str(i), 'revealed': False})
            
            random.shuffle(deck)
            st.session_state.deck = deck
            st.session_state.player_names = ['나 (User)', '알파봇 1', '알파봇 2', '알파봇 3']
            st.session_state.players = {name: [] for name in st.session_state.player_names}
            st.session_state.turn_idx = 0
            st.session_state.log = ["🎮 시스템: 최신형 AI가 탑재되었습니다. 행운을 빕니다!"]
            st.session_state.status_msg = "게임을 시작합니다!"
            st.session_state.status_type = "info"
            st.session_state.target_idx = 0 

            for name in st.session_state.player_names:
                for _ in range(6):
                    if st.session_state.deck:
                        st.session_state.players[name].append(st.session_state.deck.pop())
                DavinciCodeLogic.sort_tiles(name)

    @staticmethod
    def sort_tiles(name):
        hand = st.session_state.players[name]
        hand.sort(key=lambda x: (int(x['value']), 0 if x['color'] == 'B' else 1))

    @staticmethod
    def ai_smart_think(bot_name):
        """범위 추론 및 배제법을 사용한 초정밀 추리"""
        # 1. 이미 세상에 드러난 정보 취합
        known_numbers = []
        for name, hand in st.session_state.players.items():
            for t in hand:
                if name == bot_name or t['revealed']:
                    known_numbers.append(f"{t['color']}{t['value']}")

        # 2. 공격 대상 선정 (탈락하지 않은 사람 중)
        targets = [n for n in st.session_state.player_names if n != bot_name]
        living_targets = [n for n in targets if any(not t['revealed'] for t in st.session_state.players[n])]
        if not living_targets: return None, None, None, ""
        
        target_p = random.choice(living_targets)
        hand = st.session_state.players[target_p]
        hidden_indices = [i for i, t in enumerate(hand) if not t['revealed']]
        idx = random.choice(hidden_indices)
        target_tile = hand[idx]

        # 3. 범위 계산 (Logic Core)
        min_val = -1
        max_val = 13
        
        # 왼쪽 타일들 중 가장 가까운 공개된 값 찾기
        for i in range(idx - 1, -1, -1):
            if hand[i]['revealed']:
                min_val = int(hand[i]['value'])
                break
        # 오른쪽 타일들 중 가장 가까운 공개된 값 찾기
        for i in range(idx + 1, len(hand)):
            if hand[i]['revealed']:
                max_val = int(hand[i]['value'])
                break
        
        # 4. 후보군 추출
        possible_guesses = []
        for v in range(min_val + 1, max_val):
            # 색상 일치 여부와 이미 나온 숫자인지 체크
            if f"{target_tile['color']}{v}" not in known_numbers:
                possible_guesses.append(str(v))
        
        # 5. 최종 결정
        if not possible_guesses:
            guess = str(random.randint(0, 11))
            reason = "데이터 부족으로 찍기 수행"
        else:
            guess = random.choice(possible_guesses)
            reason = f"범위({min_val}~{max_val}) 및 공개 타일 분석 완료"

        return target_p, idx, guess, reason

    @staticmethod
    def handle_guess(attacker, defender, idx, val):
        target_hand = st.session_state.players[defender]
        target_tile = target_hand[idx]
        
        if target_tile['value'] == val:
            target_tile['revealed'] = True
            msg = f"🟢 [정답] {attacker} → {defender} ({idx+1}번 타일: {val})"
            st.session_state.log.insert(0, msg)
            st.session_state.status_msg = msg
            st.session_state.status_type = "success"
            return True
        else:
            msg = f"🔴 [오답] {attacker} → {defender} ({idx+1}번 타일을 {val}로 추리)"
            st.session_state.log.insert(0, msg)
            st.session_state.status_msg = msg
            st.session_state.status_type = "error"
            return False

# ==========================================
# 2. UI 스타일 설정
# ==========================================
st.set_page_config(page_title="Davinci Code Alpha", layout="wide")
DavinciCodeLogic.init_game()

st.markdown("""
    <style>
    .tile-container { display: flex; gap: 6px; justify-content: center; margin-bottom: 5px; }
    .tile-box {
        width: 42px; height: 70px; border-radius: 5px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; font-weight: bold; border: 2px solid #555;
    }
    .B { background: #222; color: white; }
    .W { background: #eee; color: #222; }
    .revealed { border: 3px solid #FF4B4B !important; background: #FF4B4B; color: white; }
    .target-highlight { outline: 4px solid #00FFAA; }
    .turn-area { background: rgba(0, 255, 170, 0.05); border: 2px solid #00FFAA; padding: 10px; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# 상단 상태 알림창
if st.session_state.status_type == "success": st.success(st.session_state.status_msg)
elif st.session_state.status_type == "error": st.error(st.session_state.status_msg)
else: st.info(st.session_state.status_msg)

# ==========================================
# 3. 보드 렌더링
# ==========================================
def render_board(name):
    is_me = (name == '나 (User)')
    is_current = (name == st.session_state.player_names[st.session_state.turn_idx])
    
    with st.container():
        if is_current: st.markdown('<div class="turn-area">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 6])
        c1.write(f"**{name}**")
        
        html = '<div class="tile-container">'
        for i, t in enumerate(st.session_state.players[name]):
            rev = "revealed" if t['revealed'] else ""
            target = "target-highlight" if (not is_me and name == st.session_state.get('target_p') and st.session_state.target_idx == i) else ""
            # 유저 패는 본인에게만 공개, 상대 패는 ? 처리
            display = t['value'] if (t['revealed'] or is_me) else "?"
            html += f'<div class="tile-box {t["color"]} {rev} {target}">{display}</div>'
        html += '</div>'
        c2.markdown(html, unsafe_allow_html=True)
        if is_current: st.markdown('</div>', unsafe_allow_html=True)

for name in st.session_state.player_names:
    render_board(name)

# ==========================================
# 4. 게임 제어 로직
# ==========================================
st.divider()
curr_name = st.session_state.player_names[st.session_state.turn_idx]

with st.sidebar:
    st.title("🛡️ 분석 센터")
    st.subheader("최신 로그")
    for l in st.session_state.log[:15]:
        st.write(l)
    if st.button("🔄 게임 리셋"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

if curr_name == '나 (User)':
    st.subheader("🎮 당신의 차례")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        target_p = st.selectbox("공격 대상", [n for n in st.session_state.player_names if n != '나 (User)'], key="target_p")
    with col2:
        max_idx = len(st.session_state.players[target_p])
        t_idx = st.number_input("위치", 1, max_idx, step=1) - 1
        st.session_state.target_idx = t_idx
    with col3:
        guess_v = st.text_input("숫자")

    if st.button("🚀 추리 제출", use_container_width=True):
        if guess_v.isdigit():
            hit = DavinciCodeLogic.handle_guess('나 (User)', target_p, t_idx, guess_v)
            if not hit:
                st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()

else:
    st.subheader(f"🤖 {curr_name}가 연산 중...")
    if st.button(f"{curr_name} 행동 실행", use_container_width=True):
        target_p, t_idx, g_val, reason = DavinciCodeLogic.ai_smart_think(curr_name)
        if target_p:
            # 봇의 사고 과정을 로그에 기록
            st.session_state.log.insert(0, f"🧠 {curr_name} 분석: {target_p}의 {t_idx+1}번은 {g_val}일 확률 높음 ({reason})")
            hit = DavinciCodeLogic.handle_guess(curr_name, target_p, t_idx, g_val)
            if not hit:
                st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()
