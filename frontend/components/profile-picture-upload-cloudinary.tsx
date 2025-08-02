"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Camera, X, Upload } from "lucide-react"
import { CldUploadButton } from 'next-cloudinary'
import { User } from "lucide-react"

interface ProfilePictureUploadCloudinaryProps {
    currentPictureUrl?: string | null
    onPictureUpdate: (imageUrl: string) => void
    onPictureDelete?: () => void
    isUpdating?: boolean
    isUpdatingPicture?: boolean
    isDeleting?: boolean
}

export function ProfilePictureUploadCloudinary({
    currentPictureUrl,
    onPictureUpdate,
    onPictureDelete,
    isUpdating = false,
    isUpdatingPicture = false,
    isDeleting = false,
}: ProfilePictureUploadCloudinaryProps) {
    const [isUploading, setIsUploading] = useState(false)

    const handleUploadSuccess = (result: any) => {
        console.log("Cloudinary upload successful:", result)
        setIsUploading(false)
        if (result?.info?.secure_url) {
            console.log("Calling onPictureUpdate with URL:", result.info.secure_url)
            onPictureUpdate(result.info.secure_url)
        } else {
            console.error("No secure_url in Cloudinary result:", result)
        }
    }

    const handleUploadError = (error: any) => {
        console.error("Cloudinary upload error:", error)
        setIsUploading(false)
    }

    const handleUploadStart = () => {
        console.log("Starting Cloudinary upload...")
        setIsUploading(true)

        // Add a timeout to prevent hanging
        setTimeout(() => {
            if (isUploading) {
                console.log("Upload timeout, resetting state")
                setIsUploading(false)
            }
        }, 30000) // 30 second timeout
    }

    return (
        <div className="flex flex-col items-center space-y-4">
            <div className="relative">
                {currentPictureUrl ? (
                    <img
                        src={currentPictureUrl}
                        alt="Profile"
                        className="w-24 h-24 rounded-full object-cover border-2 border-gray-200"
                    />
                ) : (
                    <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center">
                        <User className="w-8 h-8 text-gray-400" />
                    </div>
                )}
            </div>

            <div className="flex flex-col space-y-2">
                <CldUploadButton
                    className={`flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 ${isUpdatingPicture || isDeleting || isUploading || isUpdating
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
                    uploadPreset="travelstyle-profile-pictures"
                    options={{
                        maxFiles: 1,
                        resourceType: "image"
                    }}
                >
                    <Upload className="w-4 h-4 mr-2" />
                    <span>{currentPictureUrl ? 'Change Picture' : 'Upload Picture'}</span>
                </CldUploadButton>

                {(isUpdatingPicture || isDeleting || isUploading || isUpdating) && (
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                        <span>
                            {isUpdatingPicture ? "Updating profile..." :
                                isDeleting ? "Deleting..." :
                                    isUploading ? "Uploading..." :
                                        isUpdating ? "Updating..." : "Processing..."}
                        </span>
                    </div>
                )}
            </div>
        </div>
    )
}
