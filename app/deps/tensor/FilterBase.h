//
//  FilterBase.h
//  PlotDevice
//
//  Created by fish2k on 12/7/13.
//
//

#import <Foundation/Foundation.h>
#import <AppKit/AppKit.h>
#import <GPUImage/GPUImage.h>

@interface FilterBase : NSObject {
    /// GENERIC FILTER PLACEHOLDER
    GPUImageFilter *filter;
}

@property(nonatomic, retain) GPUImageFilter *filter;

- (id)init;
- (NSImage *)process:(NSImage *)input;

@end