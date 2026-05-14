import streamlit as st
import random

class DavinciCodeLogic:
    @staticmethod
    def init_game():
        """게임 초기 데이터 생성 및 세션 저장"""
        if 'deck' not in st.session_state:
            # 타일 생성: 숫자 0-11 (흑/백) + 조커(J)
            deck = []
            for color in ['B', 'W']:
                for i in range(12):
                    deck.append({'color': color, 'value': i, 'is_joker': False, 'revealed': False})
                deck.append({'color': color, 'value': 'J', 'is_joker': True, 'revealed': False})
            
            random.shuffle(deck)
            st.session_state.deck = deck
            st.session_state.p1_hand = []
            st.session_state.p2_hand = []
            st.session_state.turn = 'P1'
            st.session_state.game_over = False
            st.session_state.last_drawn = None

            # 초기 4장씩 분배
            for _ in range(4):
                st.session_state.p1_hand.append(st.session_state.deck.pop())
                st.session_state.p2_hand.append(st.session_state.deck.pop())
            
            DavinciCodeLogic.sort_tiles('p1_hand')
            DavinciCodeLogic.sort_tiles('p2_hand')

    @staticmethod
    def sort_tiles(player_hand_key):
        """다빈치 코드 정렬 규칙 적용"""
        hand = st.session_state[player_hand_key]
        # 일반 숫자는 숫자순 -> 같은 숫자면 Black 우선
        # 조커(J)는 정렬 로직에서 예외 처리가 필요하므로 일단 맨 뒤로 보냄
        # (UI에서 조커 위치 이동 기능을 위해 index를 별도로 관리하는 것이 좋음)
        
        numbers = [t for t in hand if not t['is_joker']]
        jokers = [t for t in hand if t['is_joker']]
        
        numbers.sort(key=lambda x: (x['value'], 0 if x['color'] == 'B' else 1))
        st.session_state[player_hand_key] = numbers + jokers

    @staticmethod
    def guess(target_player, tile_idx, guessed_value):
        """추리 로직: 성공 시 True, 실패 시 False 반환"""
        target_hand = st.session_state[f'{target_player.lower()}_hand']
        target_tile = target_hand[tile_idx]
        
        if str(target_tile['value']) == str(guessed_value):
            target_tile['revealed'] = True
            return True
        else:
            # 실패 시 페널티: 이번 턴에 뽑은 타일 공개
            curr_player = st.session_state.turn.lower()
            if st.session_state.last_drawn:
                for t in st.session_state[f'{curr_player}_hand']:
                    if t == st.session_state.last_drawn:
                        t['revealed'] = True
            return False

    @staticmethod
    def move_joker(player, from_idx, to_idx):
        """조커의 위치를 수동으로 변경 (다빈치 코드 핵심 규칙)"""
        hand = st.session_state[f'{player.lower()}_hand']
        tile = hand.pop(from_idx)
        hand.insert(to_idx, tile)
