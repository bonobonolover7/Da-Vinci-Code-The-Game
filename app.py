import streamlit as st
import random

# ==========================================
# 1. 게임 로직 클래스 (DavinciCodeLogic)
# ==========================================
class DavinciCodeLogic:
    @staticmethod
    def init_game():
        if 'deck' not in st.session_state:
            # 타일 생성: 0-11 (B/W) + 조커(J)
            deck = []
            for color in ['B', 'W']:
                for i in range(12):
                    deck.append({'color': color, 'value': i, 'is_joker': False, 'revealed': False})
                deck.append({'color': color, 'value': '-', 'is_joker': True, 'revealed': False})
            
            random.shuffle(deck)
            st.session_state.deck = deck
            st.session_state.p1_hand = []
            st.session_state.p2_hand = []
            st.session_state.turn = 'P1'
            st.session_state.game_over = False
            st.session_state.target_idx = 0  # UI에서 지목할 인덱스
            st.session_state.message = "게임을 시작합니다! 타일을 뽑고 상대의 숫자를 맞춰보세요."

            # 초기 4장씩 분배
            for _ in range(4):
                st.session_state.p1_hand.append(st.session_state.deck.pop())
                st.session_state.p2_hand.append(st.session_state.deck.pop())
            
            DavinciCodeLogic.sort_tiles('p1_hand')
            DavinciCodeLogic.sort_tiles('p2_hand')

    @staticmethod
    def sort_tiles(hand_key):
        hand = st.session_state[hand_key]
        numbers = [t for t in hand if not t['is_joker']]
        jokers = [t for t in hand if t['is_joker']]
        # 숫자순 정렬 -> 같으면 Black(B) 우선
        numbers.sort(key=lambda x: (x['value'], 0 if x['color'] == 'B' else 1))
        st.session_state[hand_key] = numbers + jokers

    @staticmethod
    def guess(target_idx, guessed_value):
        target_hand = st.session_state.p2_hand if st.session_state.turn == 'P1' else st.session_state.p1_hand
        target_tile = target_hand[target_idx]
        
        if str(target_tile['value']) == str(guessed_value):
            target_tile['revealed'] = True
            st.session_state.message = f"🎯 적중! {target_idx+1}번째 타일은 '{guessed_value}'였습니다."
            # 승리 체크
            if all(t['revealed'] for t in target_hand):
                st.session_state.game_over = True
                st.session_state.message = f"🏆 축하합니다! {st.session_state.turn}이 승리했습니다!"
            return True
        else:
            st.session_state.message = "❌ 틀렸습니다! 턴이 넘어갑니다."
            st.session_state.turn = 'P2' if st.session_state.turn == 'P1' else 'P1'
            return False

# ==========================================
# 2. UI 설정 및 고급 CSS
# ==========================================
st.set_page_config(page_title="Da Vinci Code Online", page_icon="🧩", layout="centered")

st.markdown("""
    <style>
    .tile-container { display: flex; gap: 10px; justify-content: center; margin: 20px 0; perspective: 1000px; }
    .flip-wrapper { width: 60px; height: 90px; perspective: 1000px; }
    .dv-tile { position: relative; width: 100%; height: 100%; text-align: center; transition: transform 0.6s; transform-style: preserve-3d; transform: rotateX(15deg); }
    .flip-wrapper:hover .dv-tile { transform: rotateX(0deg) translateY(-5px); }
    .dv-tile.is-flipped { transform: rotateY(180deg) rotateX(0deg); }
    .tile-face { position: absolute; width: 100%; height: 100%; backface-visibility: hidden; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; }
    .face-black { background: linear-gradient(145deg, #333, #000); color: white; border: 1px solid #444; }
    .face-white { background: linear-gradient(145deg, #fff, #eee); color: black; border: 1px solid #ccc; }
    .tile-back { transform: rotateY(0deg); }
    .tile-back::after { content: "?"; opacity: 0.3; }
    .tile-front { transform: rotateY(180deg); }
    .is-targeted { outline: 3px solid #00ffcc; border-radius: 8px; box-shadow: 0 0 15px #00ffcc; }
    </style>
""", unsafe_allow_html=True)

# 게임 초기화
DavinciCodeLogic.init_game()

# ==========================================
# 3. 타일 렌더링 함수
# ==========================================
def render_hand(hand, label, is_opponent=False):
    st.markdown(f"<h4 style='text-align: center;'>{label}</h4>", unsafe_allow_html=True)
    html_str = '<div class="tile-container">'
    for i, tile in enumerate(hand):
        color_class = "face-black" if tile['color'] == 'B' else "face-white"
        # 상대방 타일은 revealed일 때만 뒤집힘 / 내 타일은 항상 보임(하지만 로직상 뒤집힌 효과 유지)
        is_flipped = tile['revealed'] or (not is_opponent)
        flip_class = "is-flipped" if is_flipped else ""
        target_class = "is-targeted" if (is_opponent and st.session_state.target_idx == i) else ""
        
        # 내 타일이 공개된 경우 표시(빨간색 테두리 등 추가 가능)
        revealed_mark = "border: 2px solid red;" if (not is_opponent and tile['revealed']) else ""

        html_str += f'''
            <div class="flip-wrapper {target_class}">
                <div class="dv-tile {flip_class}">
                    <div class="tile-face tile-back {color_class}"></div>
                    <div class="tile-face tile-front {color_class}" style="{revealed_mark}">
                        <span>{tile['value']}</span>
                    </div>
                </div>
            </div>
        '''
    html_str += '</div>'
    st.markdown(html_str, unsafe_allow_html=True)

# ==========================================
# 4. 메인 화면 구성
# ==========================================
st.title("🧩 Da Vinci Code")
st.info(st.session_state.message)

# 상대방 패 (P2)
render_hand(st.session_state.p2_hand, "🤖 Opponent Hand", is_opponent=True)

st.divider()

# 내 패 (P1)
render_hand(st.session_state.p1_hand, "🧑 My Hand", is_opponent=False)

# ==========================================
# 5. 제어 UI
# ==========================================
if not st.session_state.game_over:
    cols = st.columns([2, 2, 1])
    with cols[0]:
        target = st.selectbox("지목할 상대 타일", 
                             [f"{i+1}번째" for i in range(len(st.session_state.p2_hand))],
                             index=st.session_state.target_idx)
        st.session_state.target_idx = int(target[0]) - 1
    with cols[1]:
        guess_val = st.text_input("예상 숫자 (또는 - )", value="")
    with cols[2]:
        st.write(" ") # 간격 맞춤
        if st.button("추리 실행", type="primary"):
            if guess_val:
                DavinciCodeLogic.guess(st.session_state.target_idx, guess_val)
                st.rerun()
            else:
                st.warning("숫자를 입력하세요!")

    with st.sidebar:
        st.header("📊 Game Info")
        st.write(f"**현재 턴:** {st.session_state.turn}")
        st.write(f"**남은 덱:** {len(st.session_state.deck)}개")
        if st.button("새 게임 시작"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
else:
    st.balloons()
    if st.button("다시 하기"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
