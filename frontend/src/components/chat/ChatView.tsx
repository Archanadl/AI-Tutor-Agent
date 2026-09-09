import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Send,
  Upload,
  File as FileIcon,
  Search,
  CheckCircle2,
  Plus,
  MessageSquare,
  Trash2,
} from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  source?: string;
  confidence?: number;
  source_type?: 'RAG' | 'WEB' | 'NONE';
  trace?: string[];
}

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  documentId: string | null;
  createdAt: string;
  updatedAt: string;
}

const CHAT_HISTORY_KEY = 'ai-tutor-chat-history-v2';
const CURRENT_DOCUMENT_KEY = 'ai-tutor-current-document-v2';

export const ChatView = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  /*
   * Restore the currently selected PDF immediately.
   * This survives navigation between features.
   */
  const [documentId, setDocumentId] = useState<string | null>(() => {
    try {
      return localStorage.getItem(CURRENT_DOCUMENT_KEY);
    } catch {
      return null;
    }
  });

  const [chatHistory, setChatHistory] = useState<ChatSession[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // =========================================================
  // UTILITY
  // =========================================================

  const createChatId = () => {
    return (
      Date.now().toString() +
      '-' +
      Math.random().toString(36).substring(2, 10)
    );
  };

  const getHistoryFromStorage = (): ChatSession[] => {
    try {
      const raw = localStorage.getItem(CHAT_HISTORY_KEY);

      if (!raw) {
        return [];
      }

      const parsed = JSON.parse(raw);

      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      console.error(
        'Error reading chat history:',
        error
      );

      return [];
    }
  };

  const saveHistoryToStorage = (
    history: ChatSession[]
  ) => {
    try {
      localStorage.setItem(
        CHAT_HISTORY_KEY,
        JSON.stringify(history)
      );
    } catch (error) {
      console.error(
        'Error saving chat history:',
        error
      );
    }
  };

  // =========================================================
  // LOAD HISTORY WHEN CHAT PAGE OPENS
  // =========================================================

  useEffect(() => {
    const history = getHistoryFromStorage();

    setChatHistory(history);

    /*
     * IMPORTANT:
     *
     * We intentionally start with a NEW/FRESH chat
     * whenever the Chat page is opened.
     *
     * Old chats remain in Chat History.
     */
    setMessages([]);
    setCurrentChatId(null);

    /*
     * Restore the active PDF.
     */
    try {
      const savedDocument = localStorage.getItem(
        CURRENT_DOCUMENT_KEY
      );

      if (savedDocument) {
        setDocumentId(savedDocument);
      }
    } catch (error) {
      console.error(
        'Error restoring PDF:',
        error
      );
    }
  }, []);

  // =========================================================
  // SAVE CURRENT PDF
  // =========================================================

  useEffect(() => {
    try {
      if (documentId) {
        localStorage.setItem(
          CURRENT_DOCUMENT_KEY,
          documentId
        );
      }
    } catch (error) {
      console.error(
        'Error saving current PDF:',
        error
      );
    }
  }, [documentId]);

  // =========================================================
  // SCROLL
  // =========================================================

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // =========================================================
  // SAVE CHAT DIRECTLY TO LOCAL STORAGE
  // =========================================================

  const persistChat = (
    chatId: string,
    chatMessages: Message[],
    chatDocumentId: string | null
  ) => {
    if (chatMessages.length === 0) {
      return;
    }

    try {
      const existingHistory =
        getHistoryFromStorage();

      const firstUserMessage =
        chatMessages.find(
          (message) =>
            message.role === 'user'
        );

      const title =
        firstUserMessage?.content
          ?.trim()
          .slice(0, 45) ||
        'New conversation';

      const existingChat =
        existingHistory.find(
          (chat) => chat.id === chatId
        );

      const updatedChat: ChatSession = {
        id: chatId,
        title,
        messages: chatMessages,
        documentId: chatDocumentId,
        createdAt:
          existingChat?.createdAt ||
          new Date().toISOString(),
        updatedAt:
          new Date().toISOString(),
      };

      const updatedHistory =
        existingChat
          ? existingHistory.map(
              (chat) =>
                chat.id === chatId
                  ? updatedChat
                  : chat
            )
          : [
              updatedChat,
              ...existingHistory,
            ];

      /*
       * THIS IS THE IMPORTANT FIX.
       *
       * Save directly to localStorage immediately.
       * We don't depend on a later React state effect.
       */
      saveHistoryToStorage(
        updatedHistory
      );

      setChatHistory(
        updatedHistory
      );
    } catch (error) {
      console.error(
        'Error persisting chat:',
        error
      );
    }
  };

  // =========================================================
  // FILE UPLOAD
  // =========================================================

  const handleFileUpload = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file =
      e.target.files?.[0];

    if (!file) {
      return;
    }

    /*
     * Keep the actual uploaded file for the backend.
     */
    const formData =
      new FormData();

    formData.append(
      'file',
      file
    );

    try {
      const res =
        await fetch(
          '/api/upload',
          {
            method: 'POST',
            body: formData,
          }
        );

      const data =
        await res.json();

      if (res.ok) {
        /*
         * The backend has indexed the document.
         * Save its ID/name so it survives navigation.
         */
        setDocumentId(
          data.name
        );

        localStorage.setItem(
          CURRENT_DOCUMENT_KEY,
          data.name
        );

        alert(
          `Document ${data.name} uploaded and indexed successfully.`
        );
      } else {
        alert(
          data.detail ||
            data.message ||
            'Error uploading file'
        );
      }
    } catch (error) {
      console.error(
        'Upload error:',
        error
      );

      alert(
        'Network error uploading file'
      );
    }

    /*
     * Allow the same file to be selected again.
     */
    e.target.value = '';
  };

  // =========================================================
  // SEND MESSAGE
  // =========================================================

  const handleSend = async (
    e?: React.FormEvent
  ) => {
    e?.preventDefault();

    if (
      !input.trim() ||
      isLoading
    ) {
      return;
    }

    const question =
      input.trim();

    /*
     * Create a chat ID only when
     * the user actually starts a conversation.
     */
    const chatId =
      currentChatId ||
      createChatId();

    if (!currentChatId) {
      setCurrentChatId(
        chatId
      );
    }

    const userMessage: Message = {
      role: 'user',
      content: question,
    };

    /*
     * Preserve previous messages for backend history.
     */
    const previousMessages =
      [...messages];

    /*
     * Immediately update UI.
     */
    const messagesAfterUser = [
      ...previousMessages,
      userMessage,
    ];

    setMessages(
      messagesAfterUser
    );

    /*
     * IMPORTANT:
     * Save the user message immediately.
     *
     * Even if the user navigates away before
     * the AI response finishes, the conversation
     * won't disappear.
     */
    persistChat(
      chatId,
      messagesAfterUser,
      documentId
    );

    setInput('');
    setIsLoading(true);

    try {
      const res =
        await fetch(
          '/api/chat',
          {
            method: 'POST',
            headers: {
              'Content-Type':
                'application/json',
            },
            body: JSON.stringify({
              question,
              chat_history:
                previousMessages,
              document_id:
                documentId,
            }),
          }
        );

      const data =
        await res.json();

      if (!res.ok) {
        throw new Error(
          data.detail ||
            data.message ||
            'Chat request failed'
        );
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content:
          data.answer ||
          'Sorry, I could not generate an answer.',
        source:
          data.source,
        confidence:
          data.confidence,
        source_type:
          data.source_type,
        trace:
          data.trace,
      };

      const completeMessages = [
        ...messagesAfterUser,
        assistantMessage,
      ];

      setMessages(
        completeMessages
      );

      /*
       * Save complete conversation immediately.
       */
      persistChat(
        chatId,
        completeMessages,
        documentId
      );
    } catch (error) {
      console.error(
        'Chat error:',
        error
      );

      const errorMessage: Message = {
        role: 'assistant',
        content:
          'Sorry, there was an error processing your request.',
      };

      const completeMessages = [
        ...messagesAfterUser,
        errorMessage,
      ];

      setMessages(
        completeMessages
      );

      persistChat(
        chatId,
        completeMessages,
        documentId
      );
    } finally {
      setIsLoading(false);
    }
  };

  // =========================================================
  // NEW CHAT
  // =========================================================

  const handleNewChat = () => {
    /*
     * Do NOT delete history.
     *
     * Start a completely fresh conversation.
     */
    setMessages([]);
    setInput('');
    setCurrentChatId(null);

    /*
     * IMPORTANT:
     * Keep the currently selected PDF.
     */
  };

  // =========================================================
  // RESTORE CHAT
  // =========================================================

  const handleRestoreChat = (
    chat: ChatSession
  ) => {
    setMessages(
      chat.messages || []
    );

    setCurrentChatId(
      chat.id
    );

    setInput('');

    /*
     * Restore the PDF associated
     * with that conversation.
     */
    if (chat.documentId) {
      setDocumentId(
        chat.documentId
      );

      localStorage.setItem(
        CURRENT_DOCUMENT_KEY,
        chat.documentId
      );
    } else {
      setDocumentId(null);

      localStorage.removeItem(
        CURRENT_DOCUMENT_KEY
      );
    }
  };

  // =========================================================
  // DELETE CHAT
  // =========================================================

  const handleDeleteChat = (
    e: React.MouseEvent,
    chatId: string
  ) => {
    e.stopPropagation();

    const history =
      getHistoryFromStorage();

    const updatedHistory =
      history.filter(
        (chat) =>
          chat.id !== chatId
      );

    /*
     * Delete immediately from localStorage.
     */
    saveHistoryToStorage(
      updatedHistory
    );

    setChatHistory(
      updatedHistory
    );

    if (
      currentChatId ===
      chatId
    ) {
      setMessages([]);
      setCurrentChatId(
        null
      );
    }
  };

  // =========================================================
  // FORMAT DATE
  // =========================================================

  const formatDate = (
    dateString: string
  ) => {
    try {
      return new Date(
        dateString
      ).toLocaleString(
        undefined,
        {
          day: '2-digit',
          month: 'short',
          hour: '2-digit',
          minute: '2-digit',
        }
      );
    } catch {
      return '';
    }
  };

  // =========================================================
  // UI
  // =========================================================

  return (
    <div
      style={{
        display: 'flex',
        height: '100%',
        maxWidth: '1200px',
        margin: '0 auto',
        gap: '1rem',
        minHeight: 0,
      }}
    >
      {/* ===================================================
          CHAT HISTORY
      ==================================================== */}

      <div
        style={{
          width: '230px',
          minWidth: '230px',
          display: 'flex',
          flexDirection: 'column',
          background:
            'var(--surface)',
          border:
            '1px solid var(--border)',
          borderRadius:
            'var(--radius)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            padding: '1rem',
            borderBottom:
              '1px solid var(--border)',
          }}
        >
          <button
            type="button"
            className="btn btn-primary"
            onClick={
              handleNewChat
            }
            style={{
              width: '100%',
              justifyContent:
                'center',
              fontSize:
                '0.85rem',
            }}
          >
            <Plus size={16} />
            New Chat
          </button>
        </div>

        <div
          style={{
            padding:
              '0.85rem 1rem 0.5rem',
            fontWeight: 600,
            fontSize:
              '0.85rem',
          }}
        >
          💬 Chat History
        </div>

        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding:
              '0 0.5rem 0.75rem',
          }}
        >
          {chatHistory.length ===
          0 ? (
            <div
              style={{
                padding:
                  '1rem 0.5rem',
                color:
                  'var(--muted)',
                fontSize:
                  '0.8rem',
                textAlign:
                  'center',
              }}
            >
              No previous chats yet.
            </div>
          ) : (
            chatHistory.map(
              (chat) => (
                <div
                  key={
                    chat.id
                  }
                  onClick={() =>
                    handleRestoreChat(
                      chat
                    )
                  }
                  style={{
                    padding:
                      '0.7rem',
                    marginBottom:
                      '0.4rem',
                    borderRadius:
                      '10px',
                    cursor:
                      'pointer',
                    background:
                      currentChatId ===
                      chat.id
                        ? 'var(--surface-strong)'
                        : 'transparent',
                    border:
                      currentChatId ===
                      chat.id
                        ? '1px solid var(--border)'
                        : '1px solid transparent',
                  }}
                >
                  <div
                    style={{
                      display:
                        'flex',
                      alignItems:
                        'flex-start',
                      gap:
                        '0.5rem',
                    }}
                  >
                    <MessageSquare
                      size={15}
                      style={{
                        marginTop:
                          '2px',
                        flexShrink:
                          0,
                      }}
                    />

                    <div
                      style={{
                        flex: 1,
                        minWidth: 0,
                      }}
                    >
                      <div
                        style={{
                          fontSize:
                            '0.8rem',
                          fontWeight:
                            600,
                          overflow:
                            'hidden',
                          textOverflow:
                            'ellipsis',
                          whiteSpace:
                            'nowrap',
                        }}
                      >
                        {
                          chat.title
                        }
                      </div>

                      <div
                        style={{
                          color:
                            'var(--muted)',
                          fontSize:
                            '0.68rem',
                          marginTop:
                            '3px',
                        }}
                      >
                        {formatDate(
                          chat.updatedAt
                        )}
                      </div>

                      {chat.documentId && (
                        <div
                          style={{
                            color:
                              'var(--muted)',
                            fontSize:
                              '0.65rem',
                            marginTop:
                              '3px',
                            overflow:
                              'hidden',
                            textOverflow:
                              'ellipsis',
                            whiteSpace:
                              'nowrap',
                          }}
                        >
                          📄{' '}
                          {
                            chat.documentId
                          }
                        </div>
                      )}
                    </div>

                    <button
                      type="button"
                      onClick={(
                        e
                      ) =>
                        handleDeleteChat(
                          e,
                          chat.id
                        )
                      }
                      style={{
                        border:
                          'none',
                        background:
                          'transparent',
                        cursor:
                          'pointer',
                        padding:
                          '2px',
                        color:
                          'var(--muted)',
                      }}
                      title="Delete chat"
                    >
                      <Trash2
                        size={13}
                      />
                    </button>
                  </div>
                </div>
              )
            )
          )}
        </div>
      </div>

      {/* ===================================================
          MAIN CHAT
      ==================================================== */}

      <div
        style={{
          display:
            'flex',
          flexDirection:
            'column',
          height:
            '100%',
          flex: 1,
          minWidth: 0,
        }}
      >
        {/* Header */}

        <div
          style={{
            display:
              'flex',
            justifyContent:
              'space-between',
            alignItems:
              'center',
            marginBottom:
              '1rem',
          }}
        >
          <div>
            <h2>
              💬 AI Tutor Chat
            </h2>

            <p
              style={{
                color:
                  'var(--muted)',
                fontSize:
                  '0.85rem',
              }}
            >
              {documentId
                ? `Grounded in ${documentId}`
                : 'No document loaded — web search fallback active.'}
            </p>
          </div>

          <div>
            <input
              type="file"
              id="file-upload"
              accept=".pdf"
              style={{
                display:
                  'none',
              }}
              onChange={
                handleFileUpload
              }
            />

            <label
              htmlFor="file-upload"
              className="btn btn-primary"
              style={{
                fontSize:
                  '0.85rem',
                padding:
                  '0.5rem 1rem',
                cursor:
                  'pointer',
              }}
            >
              <Upload
                size={16}
              />
              Upload PDF
            </label>
          </div>
        </div>

        {/* Messages */}

        <div
          style={{
            flex: 1,
            minHeight: 0,
            overflowY:
              'auto',
            padding:
              '1rem',
            background:
              'var(--surface)',
            borderRadius:
              'var(--radius)',
            border:
              '1px solid var(--border)',
            marginBottom:
              '1rem',
          }}
        >
          {messages.length ===
          0 ? (
            <div
              className="hero"
              style={{
                textAlign:
                  'center',
                margin:
                  '2rem',
              }}
            >
              <div className="eyebrow">
                Welcome
              </div>

              <h1>
                How can I help you{' '}
                <span className="grad-text">
                  learn
                </span>{' '}
                today?
              </h1>

              <p
                style={{
                  margin:
                    '1rem auto',
                }}
              >
                Upload a document or just
                start asking questions.
              </p>

              {documentId && (
                <div
                  style={{
                    marginTop:
                      '1rem',
                    padding:
                      '0.6rem 1rem',
                    display:
                      'inline-flex',
                    alignItems:
                      'center',
                    gap:
                      '0.5rem',
                    border:
                      '1px solid var(--border)',
                    borderRadius:
                      '99px',
                    fontSize:
                      '0.8rem',
                  }}
                >
                  <FileIcon
                    size={14}
                  />
                  {documentId}
                </div>
              )}
            </div>
          ) : (
            messages.map(
              (msg, idx) => (
                <div
                  key={idx}
                  style={{
                    marginBottom:
                      '1rem',
                    padding:
                      '1rem',
                    borderRadius:
                      '16px',
                    background:
                      msg.role ===
                      'user'
                        ? 'var(--surface-strong)'
                        : 'transparent',
                    border:
                      msg.role ===
                      'user'
                        ? '1px solid var(--border)'
                        : 'none',
                  }}
                >
                  <div
                    style={{
                      fontWeight:
                        600,
                      marginBottom:
                        '0.5rem',
                      color:
                        msg.role ===
                        'user'
                          ? 'var(--text)'
                          : 'var(--primary)',
                    }}
                  >
                    {msg.role ===
                    'user'
                      ? '🧑‍🎓 You'
                      : '🎓 Tutor'}
                  </div>

                  <div
                    style={{
                      lineHeight:
                        1.6,
                    }}
                  >
                    <ReactMarkdown>
                      {
                        msg.content
                      }
                    </ReactMarkdown>
                  </div>

                  {msg.role ===
                    'assistant' &&
                    msg.source_type &&
                    msg.source_type !==
                      'NONE' && (
                      <div
                        style={{
                          display:
                            'flex',
                          gap:
                            '0.5rem',
                          marginTop:
                            '0.75rem',
                          flexWrap:
                            'wrap',
                        }}
                      >
                        {msg.source_type ===
                        'RAG' ? (
                          <span
                            style={{
                              fontSize:
                                '0.75rem',
                              background:
                                'var(--primary)',
                              color:
                                '#000',
                              padding:
                                '2px 8px',
                              borderRadius:
                                '99px',
                              display:
                                'flex',
                              alignItems:
                                'center',
                              gap:
                                '4px',
                            }}
                          >
                            <FileIcon
                              size={
                                12
                              }
                            />
                            {
                              msg.source
                            }
                          </span>
                        ) : (
                          <span
                            style={{
                              fontSize:
                                '0.75rem',
                              background:
                                'var(--primary-2)',
                              color:
                                '#000',
                              padding:
                                '2px 8px',
                              borderRadius:
                                '99px',
                              display:
                                'flex',
                              alignItems:
                                'center',
                              gap:
                                '4px',
                            }}
                          >
                            <Search
                              size={
                                12
                              }
                            />
                            Web Search
                          </span>
                        )}

                        {msg.confidence !==
                          undefined && (
                          <span
                            style={{
                              fontSize:
                                '0.75rem',
                              border:
                                '1px solid var(--border)',
                              color:
                                'var(--muted)',
                              padding:
                                '2px 8px',
                              borderRadius:
                                '99px',
                              display:
                                'flex',
                              alignItems:
                                'center',
                              gap:
                                '4px',
                            }}
                          >
                            <CheckCircle2
                              size={
                                12
                              }
                            />
                            Confidence:{' '}
                            {
                              msg.confidence
                            }%
                          </span>
                        )}
                      </div>
                    )}
                </div>
              )
            )
          )}

          {isLoading && (
            <div
              style={{
                padding:
                  '1rem',
                color:
                  'var(--muted)',
              }}
            >
              🤖 Agent is thinking...
            </div>
          )}

          <div
            ref={
              messagesEndRef
            }
          />
        </div>

        {/* Input */}

        <form
          onSubmit={
            handleSend
          }
          style={{
            display:
              'flex',
            gap:
              '0.5rem',
          }}
        >
          <input
            type="text"
            className="input"
            placeholder="Ask a question about your study material..."
            value={
              input
            }
            onChange={(
              e
            ) =>
              setInput(
                e.target.value
              )
            }
            disabled={
              isLoading
            }
            style={{
              flex: 1,
            }}
          />

          <button
            type="submit"
            className="btn btn-primary"
            disabled={
              isLoading ||
              !input.trim()
            }
          >
            <Send
              size={18}
            />
          </button>
        </form>
      </div>
    </div>
  );
};