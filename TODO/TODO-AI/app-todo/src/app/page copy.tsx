"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Send, CheckCircle2, Clock } from "lucide-react"

interface Todo {
  id: number
  task: string
}

interface ChatMessage {
  id: string
  type: "user" | "agent"
  content: string
  timestamp: Date
}

interface ApiResponse {
  message: string
  success: boolean
}

interface TodosResponse {
  todos: Todo[]
  count: number
}

export default function TodoAIAgent() {
  const [todos, setTodos] = useState<Todo[]>([])
  const [todoCount, setTodoCount] = useState(0)
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingTodos, setIsLoadingTodos] = useState(true)
  const chatEndRef = useRef<HTMLDivElement>(null)

  // Fetch todos from API
  const fetchTodos = async () => {
    try {
      setIsLoadingTodos(true)
      const response = await fetch("http://localhost:8080/api/v1/todo/todos")
      if (response.ok) {
        const data: TodosResponse = await response.json()
        setTodos(data.todos)
        setTodoCount(data.count)
      }
    } catch (error) {
      console.error("Failed to fetch todos:", error)
    } finally {
      setIsLoadingTodos(false)
    }
  }

  // Send message to AI agent
  const sendMessage = async (userInput: string) => {
    if (!userInput.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: "user",
      content: userInput,
      timestamp: new Date(),
    }

    setChatMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      const response = await fetch("http://localhost:8080/api/v1/todo/todo", {
        method: "POST",
        headers: {
          accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_input: userInput,
        }),
      })

      if (response.ok) {
        const data: ApiResponse = await response.json()
        const agentMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: "agent",
          content: data.message,
          timestamp: new Date(),
        }
        setChatMessages((prev) => [...prev, agentMessage])

        // Refresh todos after successful operation
        await fetchTodos()
      } else {
        throw new Error("Failed to send message")
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "agent",
        content: "Sorry, I encountered an error processing your request.",
        timestamp: new Date(),
      }
      setChatMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [chatMessages])

  // Initial fetch of todos
  useEffect(() => {
    fetchTodos()
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(inputValue)
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  const cleanTaskText = (task: string) => {
    return task.replace(/^"|"$/g, "")
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Todo AI Agent</h1>
          <p className="text-gray-600 mt-2">Manage your tasks with natural language commands</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-200px)]">
          {/* Todo List - Left Side */}
          <Card className="flex flex-col">
            <CardHeader className="flex-shrink-0">
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                Your Tasks
                <Badge variant="secondary" className="ml-auto">
                  {todoCount} {todoCount === 1 ? "task" : "tasks"}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden">
              <ScrollArea className="h-full">
                {isLoadingTodos ? (
                  <div className="flex items-center justify-center h-32">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                ) : todos.length === 0 ? (
                  <div className="text-center py-12">
                    <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">No tasks yet. Ask the AI agent to add some!</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {todos.map((todo) => (
                      <div
                        key={todo.id}
                        className="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
                      >
                        <div className="flex-shrink-0">
                          <div className="w-4 h-4 rounded-full border-2 border-gray-300"></div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 break-words">{cleanTaskText(todo.task)}</p>
                        </div>
                        <Badge variant="outline" className="flex-shrink-0 text-xs">
                          #{todo.id}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Chat Interface - Right Side */}
          <Card className="flex flex-col">
            <CardHeader className="flex-shrink-0">
              <CardTitle className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                AI Agent Chat
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col overflow-hidden">
              {/* Chat Messages */}
              <ScrollArea className="flex-1 mb-4">
                <div className="space-y-4">
                  {chatMessages.length === 0 && (
                    <div className="text-center py-8">
                      <div className="bg-blue-50 rounded-lg p-4 mb-4">
                        <p className="text-sm text-blue-800">👋 Hi! I'm your Todo AI Agent. You can ask me to:</p>
                        <ul className="text-xs text-blue-700 mt-2 space-y-1">
                          <li>• Add new tasks</li>
                          <li>• Delete specific tasks</li>
                          <li>• Update existing tasks</li>
                          <li>• Organize your todo list</li>
                        </ul>
                      </div>
                    </div>
                  )}

                  {chatMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg px-4 py-2 ${
                          message.type === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
                        }`}
                      >
                        <p className="text-sm break-words">{message.content}</p>
                        <p className={`text-xs mt-1 ${message.type === "user" ? "text-blue-100" : "text-gray-500"}`}>
                          {formatTime(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}

                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 rounded-lg px-4 py-2">
                        <div className="flex items-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                          <span className="text-sm text-gray-600">AI is thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={chatEndRef} />
                </div>
              </ScrollArea>

              {/* Chat Input */}
              <form onSubmit={handleSubmit} className="flex gap-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Ask me to manage your todos..."
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button type="submit" disabled={isLoading || !inputValue.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
