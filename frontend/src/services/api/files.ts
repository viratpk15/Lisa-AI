import { apiClient } from "./apiClient"
import type { Attachment } from "@/types/api"

/**
 * File Intelligence Service Module
 * Handles multipart file uploads, attachment indexing, and parsing pipelines.
 */

/**
 * Uploads a document to the server for cognitive parsing and vectorization.
 * Binds to POST /files/upload backend endpoint.
 * 
 * @param file Binary file object selected via input or dropped.
 * @param session_id Optional conversation session to immediately bind the document to.
 * @returns Metadata object containing tokenized attachment identifiers.
 */
export const uploadDocument = async (file: File, session_id?: string): Promise<Attachment> => {
  const additionalFields = session_id ? { session_id } : undefined
  return apiClient.upload<Attachment>("/files/upload", file, "file", additionalFields)
}
