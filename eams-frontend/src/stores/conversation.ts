import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useConversationStore = defineStore('conversation', () => {
  const conversations = ref<any[]>([])
  const currentConversation = ref<any>(null)
  const messages = ref<any[]>([])

  const setConversations = (list: any[]) => {
    conversations.value = list
  }

  const setCurrentConversation = (conv: any) => {
    currentConversation.value = conv
  }

  const addMessage = (msg: any) => {
    messages.value.push(msg)
  }

  return {
    conversations,
    currentConversation,
    messages,
    setConversations,
    setCurrentConversation,
    addMessage
  }
})
