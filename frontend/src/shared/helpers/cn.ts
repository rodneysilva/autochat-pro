/**
 * Helper para combinar classes CSS.
 *
 * Usa clsx e tailwind-merge para combinar classes de forma inteligente.
 */

import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Combina classes CSS usando clsx e tailwind-merge.
 *
 * @param inputs - Classes para combinar
 * @returns String com classes combinadas
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
