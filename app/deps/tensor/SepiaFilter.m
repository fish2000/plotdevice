//
//  Filter.m
//  PlotDevice
//
//  Created by fish2k on 12/13/13.
//
//

#import "SepiaFilter.h"

@implementation SepiaFilter

@synthesize filter;

- (id)init {
    self = [super init];
    if (self) {
        filter = [GPUImageSepiaFilter init];
    }
    return self;
}

- (NSImage *)process:(NSImage *)input {
    return [filter imageByFilteringImage:input];
}

@end