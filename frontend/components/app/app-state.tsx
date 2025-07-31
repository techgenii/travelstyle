"use client"

import { useReducer, useCallback } from "react"

export type AppScreen = "home" | "chat" | "recent" | "profile" | "settings"
export type NavigationTab = "home" | "recent" | "profile"
export type ChatContext = "wardrobe" | "style" | "currency" | "general"

export interface Message {
    id: string
    text: string
    isUser: boolean
    timestamp: string
    quickReplies?: Array<{ id: string; text: string; emoji?: string }>
    showFeedback?: boolean
}

export interface AppState {
    currentScreen: AppScreen
    activeTab: NavigationTab
    chatContext: ChatContext
    messages: Message[]
    isLoading: boolean
    isAuthChecked: boolean
    mounted: boolean
    user: UserData | null
    currentSessionId: string | null
    sessionGreeting: string | null
    hasSetSessionGreeting: boolean
    messageIdCounter: number
}

type AppAction =
    | { type: 'SET_CURRENT_SCREEN'; payload: AppScreen }
    | { type: 'SET_ACTIVE_TAB'; payload: NavigationTab }
    | { type: 'SET_CHAT_CONTEXT'; payload: ChatContext }
    | { type: 'SET_MESSAGES'; payload: Message[] }
    | { type: 'ADD_MESSAGE'; payload: Message }
    | { type: 'SET_LOADING'; payload: boolean }
    | { type: 'SET_AUTH_CHECKED'; payload: boolean }
    | { type: 'SET_MOUNTED'; payload: boolean }
    | { type: 'SET_USER'; payload: UserData | null }
    | { type: 'SET_SESSION_ID'; payload: string | null }
    | { type: 'SET_SESSION_GREETING'; payload: string }
    | { type: 'SET_HAS_GREETING'; payload: boolean }
    | { type: 'INCREMENT_MESSAGE_ID' }
    | { type: 'RESET_CHAT' }

const initialState: AppState = {
    currentScreen: "home",
    activeTab: "home",
    chatContext: "general",
    messages: [],
    isLoading: false,
    isAuthChecked: false,
    mounted: false,
    user: null,
    currentSessionId: null,
    sessionGreeting: null,
    hasSetSessionGreeting: false,
    messageIdCounter: 0,
}

function appReducer(state: AppState, action: AppAction): AppState {
    switch (action.type) {
        case 'SET_CURRENT_SCREEN':
            return { ...state, currentScreen: action.payload }
        case 'SET_ACTIVE_TAB':
            return { ...state, activeTab: action.payload }
        case 'SET_CHAT_CONTEXT':
            return { ...state, chatContext: action.payload }
        case 'SET_MESSAGES':
            return { ...state, messages: action.payload }
        case 'ADD_MESSAGE':
            return { ...state, messages: [...state.messages, action.payload] }
        case 'SET_LOADING':
            return { ...state, isLoading: action.payload }
        case 'SET_AUTH_CHECKED':
            return { ...state, isAuthChecked: action.payload }
        case 'SET_MOUNTED':
            return { ...state, mounted: action.payload }
        case 'SET_USER':
            return { ...state, user: action.payload }
        case 'SET_SESSION_ID':
            return { ...state, currentSessionId: action.payload }
        case 'SET_SESSION_GREETING':
            return { ...state, sessionGreeting: action.payload }
        case 'SET_HAS_GREETING':
            return { ...state, hasSetSessionGreeting: action.payload }
        case 'INCREMENT_MESSAGE_ID':
            return { ...state, messageIdCounter: state.messageIdCounter + 1 }
        case 'RESET_CHAT':
            return {
                ...state,
                messages: [],
                chatContext: "general",
                currentSessionId: null
            }
        default:
            return state
    }
}

export function useAppState() {
    const [state, dispatch] = useReducer(appReducer, initialState)

    const generateMessageId = useCallback(() => {
        dispatch({ type: 'INCREMENT_MESSAGE_ID' })
        return `${Date.now()}-${state.messageIdCounter + 1}`
    }, [state.messageIdCounter])

    return {
        state,
        dispatch,
        generateMessageId,
    }
}
