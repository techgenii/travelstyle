"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Camera, X, Upload } from "lucide-react"
import { CldUploadButton } from 'next-cloudinary'

interface ProfilePictureUploadCloudinaryProps {
    currentPictureUrl?: string | null
    firstName: string
    lastName?: string | null
    onPictureUpdate: (imageUrl: string) => void
    onPictureDelete: () => void
    isUploading?: boolean
    isDeleting?: boolean
    isUpdatingPicture?: boolean
}

export function ProfilePictureUploadCloudinary({
    currentPictureUrl,
    firstName,
    lastName,
    onPictureUpdate,
    onPictureDelete,
    isUploading: externalIsUploading = false,
    isDeleting = false,
    isUpdatingPicture = false,
}: ProfilePictureUploadCloudinaryProps) {
    const [isUploading, setIsUploading] = useState(false)

    const handleUploadSuccess = (result: any) => {
        setIsUploading(false)
        if (result?.info?.secure_url) {
            onPictureUpdate(result.info.secure_url)
        }
    }

    const handleUploadError = (error: any) => {
        setIsUploading(false)
        console.error('Upload error:', error)
        alert('Failed to upload image. Please try again.')
    }

    const handleUploadStart = () => {
        setIsUploading(true)
    }

    const handleDelete = () => {
        onPictureDelete()
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
                        disabled={externalIsUploading || isDeleting || isUploading}
                    >
                        <X className="w-3 h-3" />
                    </Button>
                )}
            </div>

            <div className="flex flex-col items-center space-y-2">
                <CldUploadButton
                    className={`flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 ${externalIsUploading || isDeleting || isUploading || isUpdatingPicture
                        ? 'opacity-50 cursor-not-allowed'
                        : ''
                        }`}
                    onUpload={(result: any) => {
                        if (result?.error) {
                            handleUploadError(result.error)
                        } else {
                            handleUploadSuccess(result)
                        }
                    }}
                    onOpen={() => handleUploadStart()}
                    signatureEndpoint="/api/sign-cloudinary-params"
                    uploadPreset="travelstyle-profile-pictures"
                    options={{
                        maxFiles: 1,
                        resourceType: "image"
                    }}
                >
                    <Upload className="w-4 h-4 mr-2" />
                    <span>{currentPictureUrl ? 'Change Picture' : 'Upload Picture'}</span>
                </CldUploadButton>

                {(externalIsUploading || isDeleting || isUploading) && (
                    <div className="text-sm text-gray-500">
                        {isUploading ? 'Uploading...' : externalIsUploading ? 'Uploading...' : 'Deleting...'}
                    </div>
                )}
            </div>
        </div>
    )
}
