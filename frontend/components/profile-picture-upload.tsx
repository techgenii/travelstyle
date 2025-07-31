"use client"

import { useState, useRef, startTransition } from "react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Camera, X, Upload } from "lucide-react"

interface ProfilePictureUploadProps {
    currentPictureUrl?: string | null
    firstName: string
    lastName?: string | null
    onPictureUpdate: (formData: FormData) => void
    onPictureDelete: () => void
    isUploading?: boolean
    isDeleting?: boolean
}

export function ProfilePictureUpload({
    currentPictureUrl,
    firstName,
    lastName,
    onPictureUpdate,
    onPictureDelete,
    isUploading: externalIsUploading = false,
    isDeleting = false,
}: ProfilePictureUploadProps) {
    const fileInputRef = useRef<HTMLInputElement>(null)

    const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0]
        if (!file) return

        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file')
            return
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('File size must be less than 5MB')
            return
        }

        try {
            // Create a FormData object to send the file
            const formData = new FormData()
            formData.append('file', file)

            // Call the server action to upload the file within a transition
            startTransition(() => {
                onPictureUpdate(formData)
            })
        } catch (error) {
            console.error('Error uploading image:', error)
            alert('Failed to upload image. Please try again.')
        }
    }

    const handleDelete = () => {
        startTransition(() => {
            onPictureDelete()
        })
    }

    const getInitials = () => {
        const first = firstName.charAt(0).toUpperCase()
        const last = lastName ? lastName.charAt(0).toUpperCase() : ''
        return first + last
    }

    return (
        <div className="flex flex-col items-center space-y-4">
            <div className="relative">
                <Avatar className="w-24 h-24">
                    {currentPictureUrl ? (
                        <AvatarImage
                            src={currentPictureUrl}
                            alt={`${firstName} ${lastName || ''}`}
                        />
                    ) : null}
                    <AvatarFallback className="text-lg font-semibold bg-gray-200 text-gray-700">
                        {getInitials()}
                    </AvatarFallback>
                </Avatar>

                {currentPictureUrl && (
                    <Button
                        size="sm"
                        variant="destructive"
                        className="absolute -top-2 -right-2 w-6 h-6 rounded-full p-0"
                        onClick={handleDelete}
                        disabled={externalIsUploading || isDeleting}
                    >
                        <X className="w-3 h-3" />
                    </Button>
                )}
            </div>

            <div className="flex flex-col items-center space-y-2">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={externalIsUploading || isDeleting}
                    className="flex items-center space-x-2"
                >
                    <Upload className="w-4 h-4" />
                    <span>{currentPictureUrl ? 'Change Picture' : 'Upload Picture'}</span>
                </Button>

                {(externalIsUploading || isDeleting) && (
                    <div className="text-sm text-gray-500">
                        {externalIsUploading ? 'Uploading...' : 'Deleting...'}
                    </div>
                )}
            </div>

            <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
            />
        </div>
    )
}
